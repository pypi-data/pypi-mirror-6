from dexy.reporters.output import OutputReporter

class Custom(OutputReporter):
    """
    Customize the OutputReporter so there's no README file and it puts output
    in 'dexyoutput'.
    """
    aliases = ['custom']
    _settings = {
            'dir' : 'dexyoutput',
            'readme-filename' : None
            }
