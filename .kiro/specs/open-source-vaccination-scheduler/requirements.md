# Requirements Document

## Introduction

An open-source REST API that generates child vaccination schedules based on a configurable YAML-driven vaccine schedule. The system accepts a date of birth and language preference, then returns a schedule as HTML, a PNG image, or a hosted image URL. All schedule data, labels, and branding are driven entirely by configuration — no hardcoded organisation-specific content.

## Glossary

- **Vaccination Scheduler**: The Flask REST API application described in this document.
- **Vaccine Schedule**: The ordered list of vaccines and their due dates, defined in `config/vaccine_schedule.yaml`.
- **DOB**: Date of birth of the child, used as the reference date for calculating vaccine due dates.
- **Output Mode**: The format in which the schedule is returned — `html`, `image`, or `url`.
- **Config Loader**: The `utils/config_loader.py` module responsible for loading YAML and INI configuration files.
- **Schedule Service**: The `services/vacc_due_date_schedule.py` module responsible for computing due dates and rendering output.
- **Upload Folder**: A local directory where generated PNG images are temporarily stored.
- **Language Key**: A string identifier (e.g. `english`, `hindi`, `marathi`) used to select localised text from the YAML config.
- **Footer Text**: A configurable string rendered at the bottom of the generated schedule.
- **Base URL**: The publicly accessible root URL of the deployed service, used to construct image URLs.

## Requirements

### Requirement 1

**User Story:** As a developer, I want a YAML-driven vaccine schedule config, so that I can customise vaccines and labels without changing code.

#### Acceptance Criteria

1. THE Vaccination Scheduler SHALL load all vaccine entries and UI labels exclusively from `config/vaccine_schedule.yaml`.
2. WHEN a vaccine entry is missing a key for the requested language, THE Vaccination Scheduler SHALL raise a `ValueError` with a message listing the available language keys.
3. WHEN the YAML file is absent or malformed, THE Vaccination Scheduler SHALL raise a descriptive error that identifies the file path.

---

### Requirement 2

**User Story:** As an API consumer, I want to POST a date of birth and receive a vaccination schedule, so that I can integrate schedule generation into my application.

#### Acceptance Criteria

1. WHEN a POST request is made to `/vaccination/schedule` with a valid `dob` in `YYYY-MM-DD` format, THE Vaccination Scheduler SHALL return a vaccination schedule in the requested output mode.
2. WHEN the `dob` field is absent from the request body, THE Vaccination Scheduler SHALL return HTTP 400 with a JSON error message.
3. WHEN the `dob` field does not match `YYYY-MM-DD` format, THE Vaccination Scheduler SHALL return HTTP 400 with a JSON error message.
4. WHEN the `output_mode` field is not one of `html`, `image`, or `url`, THE Vaccination Scheduler SHALL return HTTP 400 with a JSON error message.
5. WHILE processing a valid request, THE Vaccination Scheduler SHALL compute each vaccine due date by adding the configured `days_after_dob` value to the provided DOB.

---

### Requirement 3

**User Story:** As an API consumer, I want to request the schedule in multiple languages, so that I can serve users in their preferred language.

#### Acceptance Criteria

1. WHEN the `lang` parameter is provided in the request body, THE Vaccination Scheduler SHALL return vaccine names and UI labels in the specified language.
2. WHEN the `lang` parameter is absent, THE Vaccination Scheduler SHALL default to `english`.
3. WHEN the `lang` value does not match any key in the YAML config, THE Vaccination Scheduler SHALL return HTTP 500 with a descriptive JSON error message.

---

### Requirement 4

**User Story:** As an API consumer, I want to receive the schedule as HTML, a PNG image, or a hosted URL, so that I can use the output in different contexts.

#### Acceptance Criteria

1. WHEN `output_mode` is `html`, THE Vaccination Scheduler SHALL return the rendered HTML schedule with `Content-Type: text/html`.
2. WHEN `output_mode` is `image`, THE Vaccination Scheduler SHALL return a PNG binary with `Content-Type: image/png` as a downloadable attachment.
3. WHEN `output_mode` is `url`, THE Vaccination Scheduler SHALL save the PNG to the upload folder and return a JSON object containing the hosted image URL.

---

### Requirement 5

**User Story:** As a system operator, I want all runtime configuration in INI and YAML files, so that I can deploy the service without modifying source code.

#### Acceptance Criteria

1. THE Vaccination Scheduler SHALL read `upload_folder`, `log_file_path`, `footer_text`, and `base_url` from `appconfig.ini` under the `[app]` section.
2. WHEN `appconfig.ini` is missing the `[app]` section, THE Vaccination Scheduler SHALL raise a `RuntimeError` with a descriptive message.
3. THE Vaccination Scheduler SHALL initialise file and console logging using the path specified in `log_file_path`.

---

### Requirement 6

**User Story:** As a developer, I want a health check endpoint, so that I can verify the service is running.

#### Acceptance Criteria

1. WHEN a GET request is made to `/vaccination/health`, THE Vaccination Scheduler SHALL return HTTP 200 with JSON body `{"status": "ok"}`.
