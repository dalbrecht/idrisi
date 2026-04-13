---
title: "Configuration"
description: "Database, map styles, server, and render defaults"
section: "getting-started"
order: 3
---

# Configuration

## Database

Idrisi uses SQLite by default. The database file is created at `idrisi.db` in the current working directory when the server starts.

The server factory accepts a `database_url` parameter if you need a different location or database:

```python
from idrisi.server import create_app

app = create_app(database_url="sqlite:////absolute/path/to/idrisi.db")
```

Default: `sqlite:///idrisi.db`

## Map Styles

Built-in styles are in the `styles/` directory:

| Style     | Description                     |
|-----------|---------------------------------|
| `default` | Clean, neutral base style       |
| `vintage` | Aged paper with muted tones     |
| `minimal` | Minimal lines, white background |
| `dark`    | Dark basemap with light labels  |

Pass any YAML file path to `--style` to use a custom style:

```bash
idrisi render "My Map" --style /path/to/my-style.yaml
```

## Server

```bash
idrisi serve --host 127.0.0.1 --port 8080
```

| Flag     | Default       | Description                   |
|----------|---------------|-------------------------------|
| `--host` | `127.0.0.1`   | Bind address                  |
| `--port` | `8080`        | Listening port                |

## Render Defaults

| Flag       | Default   | Description                            |
|------------|-----------|----------------------------------------|
| `--dpi`    | `200`     | Output resolution in dots per inch     |
| `--width`  | `1200`    | Output width in pixels                 |
| `--format` | `png`     | Output format (`png`, `pdf`, `svg`, `eps`) |
| `--style`  | `default` | Map style name or path to YAML file    |
| `--output` | `.`       | Directory to write the rendered file   |

Override any default at render time:

```bash
idrisi render "My Map" --dpi 300 --width 2400 --format pdf --output ~/Desktop
```
