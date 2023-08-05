from dexy.filter import DexyFilter

### "setting-demo"
class SettingDemo(DexyFilter):
    """
    A filter to demonstrate settings.
    """
    aliases = ['setting']
    _settings = {
            'foo' : ("The foo setting is a new setting, so it needs a docstring.", 123),
            'output' : True
            }

    def process(self):
        setting_names = sorted(self.setting_values())
        output = "\n".join("%s: %s" % (k, self.setting(k)) for k in setting_names)
        self.output_data.set_data(output)

### "subclass"
class SettingSubclassDemo(SettingDemo):
    """
    Another filter to demonstrate settings.
    """
    aliases = ['subsetting']
    _settings = {
            'foo' : 456
            }

    def process(self):
        self.output_data.set_data("The value of foo is '%s'" % self.setting('foo'))
