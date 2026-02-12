import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# create a Jinja environment for edstem xml templates
def create_ed_environment(template_folder: str) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(Path(template_folder))),
        autoescape=select_autoescape(enabled_extensions=("xml.jinja",)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

# Collapses all whitespace/newlines (used for readability) into a single line
# need to match edstem xml format
def to_edstem(template, **kwargs):
    rendered = template.render(**kwargs)
    output = re.sub(r'>\s*\n\s*', '>', rendered)
    output = re.sub(r'\s*\n\s*<', '<', output)
    output = re.sub(r'\s+', ' ', output)
    return output.strip()