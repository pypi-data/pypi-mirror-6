from os.path import join, dirname

try:
    # python 2
    from ConfigParser import RawConfigParser
except ImportError:
    # python 3
    from configparser import RawConfigParser
try:
    # python 2
    from HTMLParser import HTMLParser
except ImportError:
    # python 3
    from html.parser import HTMLParser


class Attributes(dict):
    def __getitem__( self, name ):
        try:
            return super(Attributes, self).__getitem__(name)
        except KeyError:
            return ''


class HTML2BBCode(HTMLParser):
    """
    HTML to BBCode converter

    >>> parser = HTML2BBCode()
    >>> str(parser.feed('<ul><li>one</li><li>two</li></ul>'))
    '[list][li]one[/li][li]two[/li][/list]'

    >>> str(parser.feed('<a href="http://google.com/">Google</a>'))
    '[url=http://google.com/]Google[/url]'

    >>> str(parser.feed('<img src="http://www.google.com/images/logo.png">'))
    '[img]http://www.google.com/images/logo.png[/img]'

    >>> str(parser.feed('<em>EM test</em>'))
    '[i]EM test[/i]'

    >>> str(parser.feed('<strong>Strong text</strong>'))
    '[b]Strong text[/b]'

    >>> str(parser.feed('<code>a = 10;</code>'))
    '[code]a = 10;[/code]'

    >>> str(parser.feed('<blockquote>Beautiful is better than ugly.</blockquote>'))
    '[quote]Beautiful is better than ugly.[/quote]'
    """

    def __init__(self, map=None):
        HTMLParser.__init__(self)
        self.map = RawConfigParser()
        self.map.read(join(dirname(__file__),'data/defaults.conf'))
        if map:
            self.map.read(map)

    def handle_starttag(self, tag, attrs):
        if self.map.has_section(tag):
            self.data.append(self.map.get(tag, 'start') % Attributes(attrs or {}))

    def handle_endtag(self, tag):
        if self.map.has_section(tag):
            self.data.append(self.map.get(tag, 'end'))

    def handle_data(self, data):
        self.data.append(data)

    def feed(self, data):
        self.data = []
        HTMLParser.feed(self, data)
        return u''.join(self.data)

if __name__ == '__main__':
    import doctest

    doctest.testmod()
