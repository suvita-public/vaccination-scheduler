import logging
import re
from datetime import datetime
from io import BytesIO

from flask import Blueprint, Response, jsonify, request, send_file, send_from_directory

from services.vacc_due_date_schedule import generate_vaccination_schedule_output
from utils.config_loader import get_logger, load_app_config

# Load config and initialise logger once at startup
_app_config = load_app_config()
_logger = get_logger(_app_config['log_file_path'])

vaccination_bp = Blueprint('vaccination', __name__, url_prefix='/vaccination')

_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


@vaccination_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})


@vaccination_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = _app_config['upload_folder']
    _logger.info("Serving uploaded file: %s from %s", filename, upload_folder)
    return send_from_directory(upload_folder, filename)


@vaccination_bp.route('/schedule', methods=['POST'])
def generate_vaccination_schedule_api():
    data = request.get_json(silent=True) or {}

    # Validate dob
    dob_str = data.get('dob')
    if not dob_str:
        return jsonify({"error": "dob is required"}), 400
    if not _DATE_RE.match(dob_str):
        return jsonify({"error": "dob must be in YYYY-MM-DD format"}), 400
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "dob is not a valid date"}), 400

    # Validate lang
    lang = data.get('lang', 'english')
    if not isinstance(lang, str) or not lang.strip():
        return jsonify({"error": "lang must be a non-empty string"}), 400

    name = data.get('name', '')
    child_name = data.get('child_name', 'Baby')
    output_mode = data.get('output_mode', 'html')

    if output_mode not in ('html', 'image', 'url'):
        return jsonify({"error": "output_mode must be one of: html, image, url"}), 400

    upload_folder = _app_config['upload_folder']
    footer_text = _app_config.get('footer_text', 'Vaccination Scheduler')
    base_url = _app_config.get('base_url', 'http://localhost:5000')

    try:
        output, mimetype = generate_vaccination_schedule_output(
            upload_folder=upload_folder,
            dob=dob,
            name=name,
            child_name=child_name,
            lang=lang,
            output_mode=output_mode,
            footer_text=footer_text,
            base_url=base_url,
            logger=_logger,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        _logger.exception("Unexpected error generating schedule")
        return jsonify({"error": f"Image generation failed: {e}"}), 500

    _logger.info("Schedule generated successfully, output_mode=%s", output_mode)

    if output_mode == 'image':
        return send_file(BytesIO(output), mimetype=mimetype, as_attachment=True,
                         download_name='vaccination_schedule.png')
    elif output_mode == 'url':
        return jsonify(output)
    else:
        return Response(output, mimetype=mimetype)
