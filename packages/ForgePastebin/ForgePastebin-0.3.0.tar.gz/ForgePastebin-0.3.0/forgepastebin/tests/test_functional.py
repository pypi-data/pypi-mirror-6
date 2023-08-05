from nose.tools import assert_equal
from pylons import tmpl_context as c
from ming.odm import session

from alluratest.controller import TestController
from allura.tests.decorators import with_tool
from forgepastebin import model as PM


class Test(TestController):

    def test_with_kwargs(self):
        r = self.app.get('/pastebin/?x=y')
        assert 'Recent Pastes' in r

    def test_search(self):
        r = self.app.get('/pastebin/search?q=y')
        assert 'Search Results' in r

    @with_tool('test', 'PasteBin', 'pastebin')
    def test_view(self):
        paste = PM.Paste(text='foo', creator_id=c.user._id)
        session(paste).flush(paste)
        r = self.app.get('/pastebin/%s' % paste._id, headers={'Accept': 'text/html'})
        assert_equal(r.status_int, 200)
        assert_equal(r.content_type, 'text/html')
        assert 'foo' in r.body, r.body

    @with_tool('test', 'PasteBin', 'pastebin')
    def test_embed(self):
        paste = PM.Paste(text='foo', creator_id=c.user._id)
        session(paste).flush(paste)
        r = self.app.get('/pastebin/%s.js' % paste._id, headers={'Accept': 'text/javascript'}, validate_skip=True)
        assert_equal(r.status_int, 200)
        assert_equal(r.content_type, 'text/javascript')
        assert 'foo' in r.body, r.body
