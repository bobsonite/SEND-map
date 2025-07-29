# SEND Map – Stable Version (25 May 2025)

🗂 **This file documents the current stable implementation of the SEND LA suspension map.**

## ✅ What Works

- LA polygons correctly render from `data/LASuspensionrate.geojson`
- Hovering over polygons shows tooltips with:
  - Local Authority name
  - Suspension rate (labelled field)
- Smooth and consistent tooltip behaviour
- Search bar accepts LA names (case-insensitive)
  - Typing a name and pressing **Enter** zooms to the area
  - Works even after refreshing the page (persistent)
  - Handles errors gracefully if LA not found

## ⚠️ Known Limitations

- ❌ No dropdown or autocomplete for LA names yet
- 🖱️ After zooming in, a second search may require zooming back out manually to reset viewport
- 🧭 No "Reset View" button yet
- 🔍 Only LA-level data loaded; no school-level layers yet
- ⚠️ Console warnings from `vendor.js` can be ignored for now (non-breaking)

## 💾 Version Control Notes

- Main working file: `index_working_2025-05-25.html`
- Safe to duplicate this file before testing new features:
  - e.g. `index_dropdown_test.html`, `index_zoomreset_button.html`
- Live test file for modifications: `index.html`

## 🧪 How to Run

```bash
cd /path/to/SEND-map
python3 -m http.server 8000