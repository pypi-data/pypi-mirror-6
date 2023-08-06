from StringIO import StringIO
import json
import sys
import urllib2


class Renderer(object):

    def __call__(self, statuses):
        output = StringIO()
        output.write(self.header)
        for status in statuses:
            output.write(self.render(status))
        output.write(self.footer)
        return output.getvalue()

    @property
    def header(self):
        return (u"""\
<?xml version="1.0" encoding="UTF-8"?>
<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom">
  <title>Google Plus</title>
  <id>tag:ws.plusfeed</id>""")

    @property
    def footer(self):
        return (u"""
</feed>""")

    def render(self, status):
        return (u"""\
<entry>
  <title>%(subject)s</title>
  <content type="html">%(text)s</content>
  <id>tag:ws.plusfeed:%(url)s</id>
  <published>%(created)s</published>
  <updated>%(updated)s</updated>
  <link type="text/html" href="%(url)s" rel="alternate"/>
  <author>
    <name>%(username)s</name>
  </author>
</entry>
""" % dict(text=status['object']['content'],
           subject=status['title'],
           url=status['url'],
           created=status['published'],
           updated=status['updated'],
           username=status['actor']['displayName'],
           ))


def main(argv=sys.argv):
    user_id = argv[1]
    api_key = argv[2]
    url = (
        'https://www.googleapis.com/plus/v1/people/%s/activities/public?key=%s'
        % (user_id, api_key))
    response = urllib2.urlopen(url)
    response = json.loads(response.read())
    renderer = Renderer()
    print renderer(response['items']).encode('utf8')
