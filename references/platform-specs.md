# Platform Creative Specs & Safe Zones

Universal (not localized). Every creative audit skill reads this for dimensions
and format-compliance checks.

---

## Cross-Platform Safe Zone (Vertical 9:16)

Keep critical elements (headline, logo, CTA, product shot) within **900×1000 px**
centred in a 1080×1920 canvas. This area survives feed crops across Reels,
Stories, TikTok, Shorts, and LinkedIn video.

---

## Google Ads

### Responsive Search Ads (RSA)
- Headlines: up to 15, **≥ 8 unique** recommended
- Headline length: ≤ 30 characters each
- Descriptions: up to 4, **≥ 3** recommended
- Description length: ≤ 90 characters each
- Pin sparingly — over-pinning collapses combinatorial testing

### Extensions
- Sitelinks: ≥ 4 active, each with 2 description lines
- Callouts: ≥ 4 active, ≤ 25 chars each
- Structured snippets: at least one header (Services, Brands, Models)
- Image: 1200×1200 (square) and 1200×628 (landscape), ≤ 5 MB

### Performance Max — Asset Group
- Images (1.91:1): 1200×628, minimum 5 assets
- Images (1:1): 1200×1200, minimum 5 assets
- Logos (1:1): 1200×1200, minimum 2
- Logos (4:1): 1200×300, recommended
- Videos: 16:9, 1:1, 9:16 — all three required for full placements; ≥ 10 s
- Text: 5 headlines, 5 long headlines, 5 descriptions
- Audience signals: custom segments + customer lists + demographics

---

## Meta Ads (Facebook / Instagram)

### Feed
- Square: 1080×1080 (1:1)
- Landscape: 1200×628 (1.91:1)
- Vertical Feed: 1080×1350 (4:5)
- Copy: headline ≤ 40 chars (avoid truncation), primary text ≤ 125 chars

### Stories / Reels
- Vertical: 1080×1920 (9:16)
- Video: max 15 s Stories, max 60 s Reels (Meta truncates longer)
- Keep text / CTA within central safe zone — top ~250 px and bottom ~340 px
  are covered by UI

### Carousel
- 2–10 cards, 1080×1080 each
- First card tests as the hook — put your best asset first

### Collection / Catalog
- Cover: 1200×628 or video
- Pulls from product catalog automatically

### Creative Diversity (Andromeda)
- Target ≥ 10 **genuinely distinct** creatives (different concepts, hooks,
  formats) — not 10 colour variants of the same ad
- Similarity > 60% between creatives → Andromeda suppresses delivery of the
  cluster

---

## LinkedIn Ads

### Single Image Sponsored Content
- 1200×627 (landscape) or 1080×1080 (square)
- Headline ≤ 70 chars, intro text ≤ 150 chars

### Video Sponsored Content
- 16:9, 1:1, or 9:16 (vertical support expanding)
- 3 s – 30 min (optimal 15–60 s)
- Max 200 MB, MP4 H.264

### Document Ads
- PDF ≤ 100 MB, ≤ 300 pages (optimal 8–10)
- Benchmark: 7% engagement rate

### Carousel
- 2–10 cards, 1080×1080

### Thought Leader Ads
- Posted from an employee / executive profile, promoted as Sponsored Content
- Non-employee members eligible since March 2025
- No character limits beyond the original post

---

## Video Production Standards (all platforms)

- Codec: H.264 (AVC), AAC audio, MP4 container
- Resolution: minimum 720p, preferred 1080p
- Subtitles / captions: **always include** — accessibility + sound-off viewing
  still applies in Spain
- Brand mention: within first 5 s for awareness, at CTA for performance
- Hook: first 1–3 s must earn the view (Meta, TikTok, YouTube Shorts)

---

## Google Search Console Country Targeting

Spain clients typically configure:
- Geographic target: Spain (`ES`)
- Language: Spanish (`es`) primary; Catalan (`ca`), Galician (`gl`), Basque
  (`eu`) for regional clients where relevant
- `hreflang` annotations on landing pages if bilingual

---

## Format Diversity Matrix (for creative-audit)

| Format | Google | Meta | LinkedIn |
|---|---|---|---|
| Static Image | RSA image ext. / PMax | ✅ | ✅ |
| Video | YouTube / PMax | ✅ | ✅ |
| Carousel | ❌ | ✅ | ✅ |
| Collection | ❌ | ✅ | ❌ |
| Document | ❌ | ❌ | ✅ |
| Shopping | PMax / Shopping | Catalog | ❌ |

Format diversity target: **≥ 3 active formats** per platform the client is
running on.

---

## Refresh Cadence

| Platform | Creative refresh window |
|---|---|
| Meta | 14–21 days |
| LinkedIn | 4–6 weeks |
| Google Search (RSA) | 8–12 weeks |
| YouTube | 4–8 weeks |
| PMax asset group | 8–12 weeks, swap assets in place |

Creative fatigue triggers (any one = refresh):
- CTR declines > 20% over 14 days (Meta / Google)
- Frequency > 5 (Meta prospecting) or > 12 (Meta retargeting)
- Quality Score drops ≥ 2 points (Google)
- Engagement rate drop > 30% (LinkedIn)
