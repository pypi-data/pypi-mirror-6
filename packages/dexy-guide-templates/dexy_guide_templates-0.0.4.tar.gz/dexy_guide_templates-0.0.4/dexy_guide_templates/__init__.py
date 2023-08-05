from dexy.template import Template
import os

template_dir = os.path.dirname(__file__)

prefixes = ['gs', 'cd']

for prefix in prefixes:
    templates = [f for f in os.listdir(template_dir) if f.endswith("-template") and f.startswith(prefix)]
    for f in templates:
        key = f.replace("-template", "")
        if not key in Template.plugins:
            args = {
                    'help' : "Help for %s" % key,
                    'contents-dir' : os.path.join(template_dir, "%s-template" % key)
                    }
            Template.register_plugin(key, 'Template', args)
