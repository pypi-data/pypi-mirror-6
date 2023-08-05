from __future__ import with_statement

import unittest
import types

from cwtags import tag, tagbuilder

class TestTagsTC(unittest.TestCase):

    def test_all_tags(self):
        tagnames = set(dir(tag))
        tagnames.remove('tag')
        for tname in sorted(tagnames):
            t = getattr(tag, tname)
            if not isinstance(t, types.FunctionType):
                continue
            if tname in tagbuilder.HTML_EMPTY_TAGS:
                self.assertTrue(tname in unicode(t(id='babar')))
            else:
                self.assertTrue(tname in unicode(t()))

    def test_simple_tags(self):
        self.assertEquals(unicode(tag.div(u'toto', Class="css")),
                          u'<div class="css">toto</div>')
        self.assertEquals(unicode(tag.div(u'toto',
                                          tag.p(u'titi', data_foo=42),
                                          tag.img(src='www.perdu.com'),
                                          id='foo')),
                          u'<div id="foo">toto<p data-foo="42">titi</p><img src="www.perdu.com"/></div>')

    def test_context_tags(self):
        parent = tagbuilder.UStringIO()
        with tag.div(parent.write, title=u'what it does') as d:
            d(tag.p(u'oups'))
            with tag.table(d) as t:
                t(tag.a(u'perdu !', href=u'www.perdu.com'))
                t(tag.input(type='hidden'))
        self.assertEquals(parent.getvalue(),
                          u'<div title="what it does"><p>oups</p><table>'
                          '<a href="www.perdu.com">perdu !</a><input type="hidden"/>'
                          '</table>\n</div>\n')

    def test_context_tags_withsomemethod(self):
        parent = list()
        with tag.div(parent.append, title=u'what it does') as d:
            d(tag.p(u'oups'))
            with tag.table(d) as t:
                t(tag.a(u'perdu !', href=u'www.perdu.com'))
                t(tag.input(type='hidden'))
        self.assertEquals(''.join(str(x) for x in parent),
                          u'<div title="what it does"><p>oups</p><table>'
                          '<a href="www.perdu.com">perdu !</a><input type="hidden"/>'
                          '</table>\n</div>\n')

    def _write_in_the_back(self, text):
        self.w(tag.span(text))

    def test_context_tags_interleaving(self):
        parent = tagbuilder.UStringIO()
        self.w = parent.write
        with tag.div(self.w, title='okay') as d:
            d(tag.p(u'hum'))
            self._write_in_the_back(u'uhuh')
            self.w(tag.p(u'yo'))
        self.assertEquals(parent.getvalue(),
                          u'<div title="okay"><p>hum</p><span>uhuh</span><p>yo</p></div>\n')

    def test_error(self):
        try:
            with tag.div(id=42):
                pass
        except TypeError, err:
            self.assertEqual('Did you forget to give a callable in first position ?',
                             str(err))

if __name__ == '__main__':
    unittest.main()
