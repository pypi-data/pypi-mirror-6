### "subclass"
from dexy.filter import DexyFilter

class Custom(DexyFilter):
### "docstring"
    """
    A simple custom dexy filter.
    """
### "aliases"
    aliases = ['custom']
### "settings"
    _settings = {
            'output' : True
            }

### "process-text"
    def process_text(self, input_text):
        return "dexy says: '%s'\n" % input_text.strip()
