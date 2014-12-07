
import os

from rattle import Template

TEMPLATE_DIRS = []


def select_template(templates, template_dirs=None):
    if template_dirs is None:
        template_dirs = TEMPLATE_DIRS
    if isinstance(templates, str):
        templates = [templates]
    for template in templates:
        for tdir in template_dirs:
            full_path = os.path.abspath(os.path.join(tdir, template))
            if not full_path.startswith(tdir):
                raise ValueError('Suspicious template name: %s [%s]' % (template, tdir))
            try:
                src = open(os.path.join(tdir, template), 'r').read()
            except IOError:
                pass
            else:
                return Template(src, full_path)
    raise ValueError('Not Found')
