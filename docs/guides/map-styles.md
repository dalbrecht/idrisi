---
title: "Map Styles"
description: "Built-in styles, style file anatomy, and creating custom styles"
section: "guides"
order: 4
---

# Map Styles

## Built-in Styles

Voyages ships with four styles in the `styles/` directory:

| Name | Description |
|---|---|
| `default` | Muted earth tones (`#ACBEBE` ocean, `#F4F4EF` land), clean borders, red markers |
| `vintage` | Warm, aged paper aesthetic |
| `minimal` | Minimal chrome, light palette |
| `dark` | Dark background, light features |

## Using a Style

**CLI:**

```bash
voyages render "My Map" --style vintage
```

**Web:** Select from the style dropdown in Map Composer before rendering.

## Style File Anatomy

Each style is a YAML file. The `default` style defines every available field:

```yaml
name: default
ocean: "#ACBEBE"        # Ocean/water fill color
land: "#F4F4EF"         # Land mass fill color
visited: "#A01D26"      # Visited region highlight
visited_light: "#D4737A" # Lighter visited variant
route: "#2C5F7C"        # Route line color
font: "DejaVu Sans"     # Font family for labels
borders: "#CCCCCC"      # Country/region border color
marker: "#A01D26"       # Place marker color
marker_size: 4          # Marker radius in points
title_size: 16          # Title font size
label_size: 8           # Label font size
```

## Creating a Custom Style

1. Copy a built-in style from the `styles/` directory as a starting point.
2. Modify the values you want to change.
3. Save the file with a new name (e.g., `ocean-blue.yml`).
4. Reference it by file path when rendering:

```bash
voyages render "My Map" --style ./my-styles/ocean-blue.yml
```

The style loader (`load_style()`) accepts either a built-in style name or a path to a YAML file. If the name matches one of the four built-in names (`default`, `vintage`, `minimal`, `dark`), it loads from the `styles/` directory; otherwise it treats the value as a file path.
