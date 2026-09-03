import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.video_sources = []
        self.resource_entries = []
        self.local_assets = []
        self._resource = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        for name in ("src", "href"):
            value = attributes.get(name, "")
            if value.startswith("assets/"):
                self.local_assets.append(value)
        if tag == "source" and attributes.get("type") == "video/mp4":
            self.video_sources.append(attributes.get("src"))
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
        self.assertEqual(self.parser.video_sources, ["assets/FWBC-demo.mp4"])
        video = ROOT / self.parser.video_sources[0]
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


if __name__ == "__main__":
    unittest.main()
