import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.video_sources = []
        self.images = []
        self.resource_entries = []
        self.local_assets = []
        self._resource = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        for name in ("src", "href", "data-src", "poster", "content"):
            value = attributes.get(name, "")
            if value.startswith("assets/"):
                self.local_assets.append(value)
        if tag == "source" and attributes.get("type") == "video/mp4":
            self.video_sources.append(attributes)
        if tag == "img":
            self.images.append(attributes)
        if "resource-button" in classes:
            self._resource = {"attrs": attributes, "text": []}

    def handle_data(self, data):
        if self._resource is not None:
            self._resource["text"].append(data)

    def handle_endtag(self, tag):
        if tag in {"a", "span"} and self._resource is not None:
            self._resource["text"] = " ".join(
                "".join(self._resource["text"]).split()
            )
            self.resource_entries.append(self._resource)
            self._resource = None


class SitePublishingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SiteParser()
        cls.parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    def test_demo_video_is_browser_compatible_and_linked(self):
        self.assertEqual(len(self.parser.video_sources), 1)
        source = self.parser.video_sources[0]
        self.assertNotIn("src", source)
        self.assertEqual(source.get("data-src"), "assets/FWBC-demo.mp4")
        video = ROOT / source["data-src"]
        self.assertTrue(video.is_file(), "Demo video is missing")
        self.assertLess(video.stat().st_size, 100_000_000)

        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,codec_name,width,height",
                "-of",
                "json",
                str(video),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        streams = json.loads(probe.stdout)["streams"]
        video_stream = next(s for s in streams if s["codec_type"] == "video")
        audio_stream = next(s for s in streams if s["codec_type"] == "audio")
        self.assertEqual(video_stream["codec_name"], "h264")
        self.assertLessEqual(video_stream["height"], 720)
        self.assertEqual(audio_stream["codec_name"], "aac")

    def test_video_source_is_attached_only_after_user_click(self):
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "test_video_lazy_load.js")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_page_images_use_webp_and_below_fold_images_are_lazy(self):
        for image in self.parser.images:
            source = image["src"]
            if source.endswith(".svg"):
                continue
            self.assertTrue(source.endswith(".webp"), source)
            if not source.startswith("assets/logos/"):
                self.assertEqual(image.get("loading"), "lazy", source)

    def test_only_video_resource_is_released(self):
        resources = {entry["text"]: entry["attrs"] for entry in self.parser.resource_entries}

        self.assertIn("Video", resources)
        video = resources["Video"]
        self.assertEqual(video.get("href"), "assets/FWBC-demo.mp4")
        self.assertNotIn("disabled", video.get("class", "").split())
        self.assertNotIn("aria-disabled", video)

        for label in ("ArXiv coming soon", "Code coming soon", "Dataset coming soon"):
            entry = resources[label]
            self.assertIn("disabled", entry.get("class", "").split())
            self.assertEqual(entry.get("aria-disabled"), "true")

    def test_all_local_page_assets_exist(self):
        missing = [asset for asset in self.parser.local_assets if not (ROOT / asset).is_file()]
        self.assertEqual(missing, [])

    def test_css_image_assets_exist_and_use_webp(self):
        css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
        sources = re.findall(r'url\(["\']?([^"\')]+)', css)

        for source in sources:
            if source.startswith(("data:", "http://", "https://")):
                continue
            asset = ROOT / "assets" / source
            self.assertTrue(asset.is_file(), source)
            self.assertTrue(source.endswith((".webp", ".svg")), source)

    def test_search_metadata_uses_canonical_absolute_urls(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        canonical = "https://ytydt-reuz.github.io/FWBC-VLA/"

        self.assertIn(
            "<title>FWBC-VLA: Force-Aware Whole-Body Compensation for Contact-Rich Loco-Manipulation</title>",
            html,
        )
        self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
        self.assertIn(f'<meta property="og:url" content="{canonical}">', html)
        self.assertIn(
            '<meta property="og:image" content="https://ytydt-reuz.github.io/FWBC-VLA/assets/FWBC-poster.webp">',
            html,
        )
        self.assertIn('<meta name="robots" content="index, follow, max-image-preview:large">', html)

    def test_scholarly_article_metadata_matches_visible_page(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        metadata = json.loads(match.group(1))

        article = metadata["mainEntity"]
        self.assertEqual(metadata["@type"], "WebPage")
        self.assertEqual(article["@type"], "ScholarlyArticle")
        self.assertEqual(article["headline"], "FWBC-VLA: Force-Aware Whole-Body Compensation for Contact-Rich Loco-Manipulation")
        self.assertEqual(len(article["author"]), 9)
        self.assertNotIn("sameAs", article)

    def test_sitemap_and_indexnow_ownership_files_are_valid(self):
        sitemap = ET.parse(ROOT / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        location = sitemap.findtext("s:url/s:loc", namespaces=namespace)
        self.assertEqual(location, "https://ytydt-reuz.github.io/FWBC-VLA/")

        key_files = [
            path
            for path in ROOT.glob("*.txt")
            if re.fullmatch(r"[0-9a-f]{32}\.txt", path.name)
        ]
        self.assertEqual(len(key_files), 1)
        self.assertEqual(key_files[0].read_text(encoding="utf-8").strip(), key_files[0].stem)


if __name__ == "__main__":
    unittest.main()
