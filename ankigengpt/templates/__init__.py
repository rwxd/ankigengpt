from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

TEMPLATES_DIR = Path(__file__).parent.absolute()
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False, loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=False
)

template_kindle: Template = TEMPLATE_ENVIRONMENT.get_template('kindle.j2')
template_epub: Template = TEMPLATE_ENVIRONMENT.get_template('epub.j2')
template_plain: Template = TEMPLATE_ENVIRONMENT.get_template('plain.j2')
