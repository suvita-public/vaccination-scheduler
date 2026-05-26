# Implementation Plan

- [x] 1. Scaffold project structure
  - Create directory layout: routes/, services/, utils/, config/, templates/, tests/, static/, logs/, vaccination-calendar/
  - Add placeholder `__init__.py` files, `app.py`, `appconfig.ini`, `logconfig_calendarservice.ini`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`
  - _Requirements: 5.1, 5.3_

- [x] 2. Refactor `utils/config_loader.py`





  - [ ] 2.1 Make `load_vaccine_schedule` accept an optional `config_path` parameter defaulting to the project-root-relative path
    - Remove `os.path.dirname(__file__)` relative resolution; resolve from `os getcwd()` or an explicit default

    - Raise `FileNotFoundError` with the resolved path when the file is absent
    - _Requirements: 1.1, 1.3_
  - [ ] 2.2 Make `load_app_config` accept an optional `config_path` parameter defaulting to `"appconfig.ini"`
    - _Requirements: 5.1, 5.2_
  - [ ]* 2.3 Write unit tests for `config_loader` in `tests/test_config_loader.py`
    - Test `load_vaccine_schedule` with valid YAML, missing file, and malformed YAML
    - Test `load_app_config` with valid INI and missing `[app]` section
    - _Requirements: 1.3, 5.2_

- [ ] 3. Implement `services/vacc_due_date_schedule.py`
  - [ ] 3.1 Verify `generate_vaccination_schedule` raises `ValueError` for unknown language keys
    - Confirm error message lists available keys
    - _Requirements: 1.2, 3.3_
  - [ ] 3.2 Verify `generate_vaccination_schedule_output` passes `footer_text` and `base_url` through correctly
    - _Requirements: 4.1, 4.2, 4.3, 5.1_
  - [ ]* 3.3 Write unit tests for schedule service in `tests/test_schedule_service.py`
    - Test due date calculation for at least two vaccine entries
    - Test `ValueError` raised for unknown language
    - Test HTML output contains expected labels
    - _Requirements: 1.2, 2.5, 3.1_

- [ ] 4. Implement `routes/vaccination_routes.py`
  - [ ] 4.1 Ensure all input validation (dob format, output_mode enum, lang type) returns HTTP 400 with JSON error
    - _Requirements: 2.2, 2.3, 2.4_
  - [ ] 4.2 Wire `footer_text` and `base_url` from `_app_config` into the service call
    - _Requirements: 4.3, 5.1_
  - [ ] 4.3 Confirm `/vaccination/health` returns `{"status": "ok"}` with HTTP 200
    - _Requirements: 6.1_
  - [ ]* 4.4 Write route integration tests in `tests/test_routes.py` using Flask test client
    - Test health endpoint
    - Test valid schedule POST for html, image, and url output modes
    - Test 400 responses for missing/invalid dob and invalid output_mode
    - Test 500 response for unknown lang
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.3, 4.1, 4.2, 4.3, 6.1_

- [ ] 5. Wire everything together in `app.py`
  - Confirm `register_routes` is called and Waitress serves on `0.0.0.0:5000`
  - _Requirements: 5.3_
