import ConfigParser, cStringIO, textwrap

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        return ()

    update = install

    def __setitem__(self, name, data):
        data = dict(stringify(name, i) for i in data.items())
        self.buildout._raw[name] = data
        self.buildout[name]

    def parse(self, data):
        parser = ConfigParser.RawConfigParser()
        parser.readfp(cStringIO.StringIO(textwrap.dedent(data)))
        buildout = self.buildout
        raw = buildout._raw
        sections = sorted(parser.sections())

        for section in sections:
            raw[section] = dict(parser.items(section))
        for section in sections:
            buildout[section]

validtypes = unicode, int

def stringify(section, (key, value)):
    if not isinstance(value, str):
        if isinstance(value, validtypes):
            value = str(value)
        else:
            raise TypeError("Invalid type: %s for %s:%s, %r" %
                            (type(value), section, key, value))
    return key, value
