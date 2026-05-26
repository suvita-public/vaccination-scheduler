# Vaccination Scheduler API

An open-source REST API that generates child vaccination schedules based on a configurable YAML-driven vaccine schedule. Supports multilingual output and returns results as HTML, a PNG image, or a hosted image URL.

All schedule data, labels, and branding are driven entirely by configuration — no hardcoded organisation-specific content.

## Features

- YAML-driven vaccine schedule — add, remove, or edit vaccines without touching code
- Multilingual support (English, Hindi, Marathi out of the box — extend via YAML)
- Three output modes: `html`, `image` (PNG download), `url` (hosted PNG link)
- Configurable footer text and base URL via `appconfig.ini`
- Served by [Waitress](https://docs.pylonsproject.org/projects/waitress/) — production-ready WSGI server
- Docker support included

## Stack

- Python 3.11
- Flask 3
- Waitress
- html2image (Chromium headless)
- PyYAML
- Jinja2
- pytest

## Quick Start

### Local

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the app
#    Edit appconfig.ini — set upload_folder, footer_text, base_url as needed

# 4. Run
python app.py
```

The API will be available at `http://localhost:5000`.

### Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8080`.

## Configuration

### `appconfig.ini`

```ini
[app]
log_file_path  = ./logconfig_calendarservice.ini
upload_folder  = ./vaccination-calendar
footer_text    = Vaccination Scheduler
base_url       = http://localhost:5000
```

| Key | Description |
|---|---|
| `log_file_path` | Path to the logging INI config |
| `upload_folder` | Directory where generated PNG images are stored |
| `footer_text` | Text shown at the bottom of every generated schedule |
| `base_url` | Root URL used to construct image URLs when `output_mode=url` |

### `config/vaccine_schedule.yaml`

Defines the vaccine schedule and all UI labels. Each vaccine entry requires:

```yaml
vaccine_schedule:
  - age:
      english: "Birth"
      hindi: "जन्म"
    days_after_dob: 0
    name:
      english: "BCG, OPV-0, Hepatitis B birth dose"
      hindi: "..."

labels:
  child_name:
    english: "Child's Name"
    hindi: "बच्चे का नाम"
  # ... other label keys
```

To add a new language, add a new key under every `age`, `name`, and `labels` entry in the YAML.

## API Reference

### `GET /vaccination/health`

Returns service status.

**Response**
```json
{"status": "ok"}
```

---

### `POST /vaccination/schedule`

Generates a vaccination schedule for a child.

**Request body**

```json
{
  "dob": "2024-01-15",
  "lang": "english",
  "name": "Parent Name",
  "child_name": "Baby",
  "output_mode": "html"
}
```

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `dob` | string | yes | — | `YYYY-MM-DD` format |
| `lang` | string | no | `english` | Must match a language key in the YAML |
| `name` | string | no | `""` | Parent/guardian name |
| `child_name` | string | no | `Baby` | Child's name shown on the schedule |
| `output_mode` | string | no | `html` | One of `html`, `image`, `url` |

**Responses**

| `output_mode` | Content-Type | Body |
|---|---|---|
| `html` | `text/html` | Rendered HTML schedule |
| `image` | `image/png` | PNG file download |
| `url` | `application/json` | `{"url": "http://..."}` |

**Error responses**

| Scenario | Status | Body |
|---|---|---|
| Missing `dob` | 400 | `{"error": "dob is required"}` |
| Invalid `dob` format | 400 | `{"error": "dob must be in YYYY-MM-DD format"}` |
| Invalid `output_mode` | 400 | `{"error": "output_mode must be one of: html, image, url"}` |
| Unknown `lang` | 500 | `{"error": "Language key '...' not found ..."}` |

---

### `GET /vaccination/uploads/<filename>`

Serves a previously generated PNG image (used with `output_mode=url`).

## Running Tests

```bash
pytest
```

## Project Structure

```
.
├── app.py                          # Entry point
├── appconfig.ini                   # Runtime configuration
├── logconfig_calendarservice.ini   # Logging configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── config/
│   └── vaccine_schedule.yaml       # Vaccine schedule and labels
├── routes/
│   └── vaccination_routes.py       # Flask Blueprint and endpoints
├── services/
│   └── vacc_due_date_schedule.py   # Schedule computation and rendering
├── utils/
│   └── config_loader.py            # YAML/INI config loading
├── templates/
│   └── vaccination_schedule.html   # Jinja2 HTML template
├── static/
│   └── styles.css
├── tests/
├── logs/                           # Generated at runtime (gitignored)
└── vaccination-calendar/           # Generated images (gitignored)
```

## License

MIT
