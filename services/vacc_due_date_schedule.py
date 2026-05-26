from jinja2 import Environment, FileSystemLoader
import os
from datetime import timedelta
from utils.config_loader import load_vaccine_schedule
from html2image import Html2Image
import uuid


def generate_vaccination_schedule(dob, lang):
    """Calculate due dates for all vaccines in the YAML config for a given reference date and language."""
    config = load_vaccine_schedule()
    schedule = []

    for vaccine in config['vaccine_schedule']:
        try:
            age_label = vaccine['age'][lang]
            vaccine_name = vaccine['name'][lang]
        except KeyError:
            raise ValueError(
                f"Language key '{lang}' not found in vaccine config. "
                f"Available languages: {list(vaccine['age'].keys())}"
            )
        due_date = dob + timedelta(days=vaccine['days_after_dob'])
        schedule.append((age_label, vaccine_name, due_date.strftime("%Y-%m-%d")))

    try:
        labels = {key: value[lang] for key, value in config['labels'].items()}
    except KeyError:
        raise ValueError(f"Language key '{lang}' not found in labels config.")

    return schedule, labels


def generate_html(schedule, labels, name, child_name, dob, footer_text):
    """Render the vaccination schedule as HTML using the Jinja2 template."""
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('vaccination_schedule.html')
    return template.render(
        schedule=schedule,
        labels=labels,
        name=name,
        child_name=child_name,
        dob=dob,
        footer_text=footer_text,
    )


def generate_image_from_html(html_content, output_path, logger):
    """Render HTML content to a PNG image using Chromium via html2image."""
    hti = Html2Image(
        custom_flags=[
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-software-rasterizer",
            "--no-default-browser-check",
        ]
    )
    temp_html_path = os.path.join(os.getcwd(), 'temp.html')
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    try:
        hti.output_path = os.path.dirname(output_path)
        hti.screenshot(html_file=temp_html_path, save_as=os.path.basename(output_path), size=(900, 900))
        logger.info("Image saved: %s", output_path)
    finally:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)


def generate_vaccination_schedule_output(upload_folder, dob, name='', child_name='Baby',
                                         lang='english', output_mode='html',
                                         footer_text='Vaccination Scheduler',
                                         base_url='http://localhost:5000', logger=None):
    """Orchestrate schedule generation and return output in the requested format."""
    schedule, labels = generate_vaccination_schedule(dob, lang)
    html = generate_html(schedule, labels, name, child_name, dob.strftime('%Y-%m-%d'), footer_text)

    if output_mode in ('image', 'url'):
        unique_filename = f'vaccination_schedule_{uuid.uuid4()}.png'
        output_path = os.path.join(upload_folder, unique_filename)
        generate_image_from_html(html, output_path, logger)

        if output_mode == 'image':
            with open(output_path, 'rb') as img_file:
                img = img_file.read()
            os.remove(output_path)
            return img, 'image/png'
        else:
            image_url = f'{base_url.rstrip("/")}/vaccination/uploads/{unique_filename}'
            return {'url': image_url}, 'application/json'

    return html, 'text/html'
