# FWBC-VLA Project Page Design

Date: 2026-08-15

## Goal

Build a GitHub Pages-ready paper project homepage for FWBC-VLA under the dedicated `homepage/` directory. The page should present the paper cleanly now, while leaving Paper, Video, Code, and Dataset resources easy to activate later as public links become available.

## Publishing Target

- Source directory: `/home/yt/Force_lite/homepage`
- GitHub Pages setting: deploy this directory through the chosen publishing workflow. Standard GitHub Pages branch settings expose only repository root or `docs/`, so `homepage/` should be published with GitHub Actions or copied to the Pages source during release.
- Implementation type: static HTML/CSS/JS only. No npm build step, no React/Vite dependency, and no server requirement.

## Content Source

Use the current paper source as the authority for:

- Title: `FWBC-VLA: Force-Aware Whole-Body Compensation for Contact-Rich Loco-Manipulation`
- Authors, affiliation numbers, equal-contribution markers, and corresponding-author markers from `paper/main.tex`
- Abstract from `paper/main.tex`
- Figures from `paper/Pics/`
- PDF from `paper/build-aaai27/main.pdf` if present, otherwise `paper/main.pdf`

## Page Structure

1. Header / hero
   - Paper title.
   - Author list with affiliation superscripts.
   - Affiliation list.
   - Short venue/status line if available; otherwise omit.

2. Resource buttons
   - `ArXiv`: visible but disabled or marked `Coming soon` until the public arXiv URL is available.
   - `Video`: visible but disabled or marked `Coming soon`.
   - `Code`: visible but disabled or marked `Coming soon`, using a GitHub-style icon.
   - `Dataset`: visible but disabled or marked `Coming soon`, using a Hugging Face-style icon.
   - `BibTeX`: anchor link to the BibTeX section.

3. Demo
   - Add a large video placeholder block before the overview.
   - Keep the block ready for a YouTube, Bilibili, or direct MP4 embed after release.

4. Teaser
   - Use a strong paper visual, preferably `paper/Pics/framework.png`.
   - Include a concise caption describing the force-aware interface between VLA and WBC.

5. Abstract
   - Use the current abstract, lightly formatted for web readability without changing technical claims.

6. Method overview
   - Three compact blocks:
     - HSR-Force sensorless interaction estimation.
     - Force-conditioned VLA action generation.
     - Body compensation for whole-body control.

7. Results
   - Include available paper figures such as real-world experiments and force-estimation visuals.

8. BibTeX
   - Include a placeholder BibTeX entry with the current title and authors.
   - Mark venue/year fields as update targets if final publication metadata is unavailable.

9. Footer
   - Brief note that code, dataset, and videos will be linked when released.

## Visual Direction

Reference `https://unified-force.github.io/` for academic project-page structure: centered title, author block, resource buttons, large teaser, abstract, video/body sections, and BibTeX. Do not copy its bundled React implementation. Use a restrained white-background academic style with blue/teal accents, readable typography, responsive layout, and image-first sections.

## Assets

Create a small asset set under `homepage/assets/`:

- `homepage/assets/framework.png`
- Optional result images copied from:
  - `paper/Pics/Realworld_exp_300dpi.png`
  - `paper/Pics/Force_estimate.png`
  - `paper/Pics/force_effect.png`

Do not upload or link private source code, private datasets, or unpublished videos.

## Error Handling and Degradation

- Render ArXiv as `Coming soon` until the public arXiv URL is available.
- If a figure is missing, omit that visual block rather than showing a broken image.
- External links for unavailable resources should not point to dummy URLs.

## Validation

- Open the page locally from `homepage/index.html` or via a simple static server.
- Check desktop and mobile viewport layout.
- Confirm all local image and PDF links resolve.
- Confirm `Coming soon` buttons are visibly non-clickable or clearly marked.

## Out of Scope

- No source-code publication.
- No dataset publication.
- No hosted video integration until a public video URL is provided.
- No custom domain configuration unless requested later.
