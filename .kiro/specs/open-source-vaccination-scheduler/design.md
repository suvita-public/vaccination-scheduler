# Design Document

## Overview

The Vaccination Scheduler is a lightweight Flask REST API that computes child vaccination due dates from a configurable YAML schedule. It supports multilingual output and can return results as HTML, a PNG image, or a hosted image URL. All configuration — vaccines, labels, branding, paths — lives in `config/vaccine_schedule.yaml` and `appconfig.ini`. There is no hardcoded organisation content.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Flask App (app.py)                │
│                  served by Waitress                  │
└────────────────────────┬────────────────────────────┘
                         │ register_routes
                         ▼
┌─────────────────────────────────────────────────────┐
│          Blueprint: vaccination_bp                   │
│          routes/vaccination_routes.py                │
│  GET  /vaccination/health                            │
│  POST /vaccination/schedule                          │
│  GET  /vaccination/uploads/<filename>                │
└────────────┬────────────────────────────────────────┘
             │ calls
             ▼
┌─────────────────────────────────────────────────────┐
│        Schedule Service                              │
│        services/vacc_due_date_schedule.py            │
│  generate_vaccination_schedule()                     │
│  generate_html()                                     │
│  generate_image_from_html()                          │
│  generate_vaccination_schedule_output()              │
└────────────┬────────────────────────────────────────┘
             │ calls
             ▼
┌─────────────────────────────────────────────────────┐
│        Config Loader                                 │
│        utils/config_loader.py                        │
│  load_vaccine_schedule()  → YAML                     │
│  load_app_config()        → INI                      │
│  get_logger()             → logging                  │
└─────────────────────────────────────────────────────┘
```

---

## Components and Interfaces

### `utils/config_loader.py`

Responsible for all configuration I/O. Must be side-effect-free and raise clear errors on misconfiguration.

| Function | Signature | Returns | Raises |
|---|---|---|---|
| `load_vaccine_schedule` | `(config_path: str = None) -> dict` | Parsed YAML dict | `FileNotFoundError`, `yaml.YAMLError` |
| `load_app_config` | `(config_path: str = None) -> dict` | `[app]` section as dict | `RuntimeError` if section missing |
| `get_logger` | `(log_file_path: str) -> Logger` | `logging.Logger` | propagates logging errors |

- `config_path` defaults allow callers to override paths (useful in tests).
- `load_vaccine_schedule` resolves the YAML path relative to the project root, not `__file__`, to avoid path issues when running from different working directories.

### `services/vacc_due_date_schedule.py`

Orchestrates schedule computation and rendering.

| Function | Purpose |
|---|---|
| `generate_vaccination_schedule(dob, lang)` | Returns `(schedule_rows, labels)` |
| `generate_html(schedule, labels, ...)` | Renders Jinja2 template |
| `generate_image_from_html(html, output_path, logger)` | Writes PNG via html2image/Chromium |
| `generate_vaccination_schedule_output(...)` | Top-level orchestrator; returns `(output, mimetype)` |

### `routes/vaccination_routes.py`

Flask Blueprint with three endpoints. Validates all inputs before delegating to the service layer. Loads config and logger once at module import time.

### `app.py`

Entry point. Creates the Flask app, registers the blueprint, and starts Waitress.

---

## Data Models

### Request body — `POST /vaccination/schedule`

```json
{
  "dob": "2024-01-15",
  "lang": "english",
  "name": "Parent Name",
  "child_name": "Baby",
  "output_mode": "html"
}
```

| Field | Type | Required | Default | Validation |
|---|---|---|---|---|
| `dob` | string | yes | — | `YYYY-MM-DD`, valid calendar date |
| `lang` | string | no | `english` | non-empty string; must match a key in YAML |
| `name` | string | no | `""` | — |
| `child_name` | string | no | `"Baby"` | — |
| `output_mode` | string | no | `"html"` | one of `html`, `image`, `url` |

### `vaccine_schedule.yaml` structure

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
    hindi: "..."
  # ... other label keys
```

### `appconfig.ini` structure

```ini
[app]
log_file_path = ./logconfig_calendarservice.ini
upload_folder = ./vaccination-calendar
footer_text = Vaccination Scheduler
base_url = http://localhost:5000
```

---

## Error Handling

| Scenario | HTTP Status | Response |
|---|---|---|
| Missing `dob` | 400 | `{"error": "dob is required"}` |
| Invalid `dob` format | 400 | `{"error": "dob must be in YYYY-MM-DD format"}` |
| Invalid calendar date | 400 | `{"error": "dob is not a valid date"}` |
| Invalid `output_mode` | 400 | `{"error": "output_mode must be one of: html, image, url"}` |
| Unknown `lang` key | 500 | `{"error": "Language key '...' not found ..."}` |
| Image generation failure | 500 | `{"error": "Image generation failed: ..."}` |
| Missing `[app]` in INI | startup crash | `RuntimeError` with message |
| Missing/malformed YAML | runtime | `FileNotFoundError` / `yaml.YAMLError` |

---

## Testing Strategy

Tests live in `tests/` and use `pytest`. The Flask test client is used for route-level tests.

- `tests/test_config_loader.py` — unit tests for `load_vaccine_schedule`, `load_app_config`, `get_logger`
- `tests/test_schedule_service.py` — unit tests for `generate_vaccination_schedule`, `generate_html`
- `tests/test_routes.py` — integration tests for all three endpoints using Flask test client

Key test scenarios:
- Valid schedule generation for each supported language
- Missing / malformed `dob` returns 400
- Unknown `lang` returns 500
- Health check returns 200
- Config loader raises correct errors on bad input
