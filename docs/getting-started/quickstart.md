---
title: "Quick Start"
description: "Add places, create a trip, and render your first map"
section: "getting-started"
order: 2
---

# Quick Start

Choose the track that matches how you prefer to work. Both produce the same result — a rendered travel map.

---

## CLI Track

**1. Add places:**

```bash
voyages place add --name "Paris" --lat 48.8566 --lon 2.3522
voyages place add --name "Rome" --lat 41.9028 --lon 12.4964
```

**2. Create a trip:**

```bash
voyages trip create "Europe 2025"
```

**3. Create a project:**

```bash
voyages project create "My First Map" --map-type travel
```

**4. Render the map:**

```bash
voyages render "My First Map" --style vintage --format png --output .
```

**5. Open the output:**

```bash
# macOS
open "My First Map.png"

# Linux
xdg-open "My First Map.png"
```

---

## Web Track

**1. Start the server:**

```bash
voyages serve
```

Open `http://127.0.0.1:8080`.

**2. Add places:**

Navigate to **Places**. Use the search box to find "Paris" via Nominatim, then click **Add**. Repeat for "Rome".

**3. Create a trip:**

Navigate to **Trips**. Click **New Trip**, enter "Europe 2025", and save.

**4. Create a project:**

Navigate to **Map Composer**. Click **New Project**, enter a name, select **travel** as the map type, then choose a style.

**5. Render and download:**

Click **Render**. When the render completes, click **Download** to save the PNG.

---

## Next Steps

- [CLI Workflow](cli-workflow.md) — full reference for all CLI subcommands
- [Web Workflow](web-workflow.md) — walkthrough of the web UI features
