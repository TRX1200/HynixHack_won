# vision inventory — 7 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`image-annotation`](../recipes/image-annotation.md) | Annotate existing images | Pillow shapes and labels on original | Bounding boxes inside image, original preserved |
| [`image-registration`](../recipes/image-registration.md) | Image alignment before comparison | Translation/feature-based registration | Known transform synthetic test and residual |
| [`image-segmentation`](../recipes/image-segmentation.md) | Region segmentation | Threshold + morphology baseline | IoU on labeled synthetic masks |
| [`image-measure`](../recipes/image-measure.md) | Pixel geometry to physical measure | Measure pixels with explicit calibration | Known-size object and unit test |
| [`image-compare`](../recipes/image-compare.md) | Compare reference and observed image | Normalize exposure and register then diff | No-change/shift-only/real-change negative controls |
| [`ocr-read`](../recipes/ocr-read.md) | Extract text from images | Use provided selectable text if present | Spot-check OCR outputs and numeric tokens |
| [`synthetic-graphic`](../recipes/synthetic-graphic.md) | Create code-rendered diagram | SVG/Pillow deterministic geometry | Render and inspect visual output |
