import logging
import urlparse

# Non-stdlib imports
import pymongo

from bson import ObjectId
from bson.errors import InvalidId
from tg import expose, redirect
from pylons import tmpl_context as c, app_globals as g
from pylons import request
from webob import exc
from paste.deploy.converters import asbool
from tg.decorators import with_trailing_slash, without_trailing_slash
from tg.controllers import CUSTOM_CONTENT_TYPE
import ew.jinja2_ew as ew
import json

# Pyforge-specific imports
from allura import model as M
from allura.app import Application, SitemapEntry, DefaultAdminController
from allura.app import ConfigOption
from allura.controllers import BaseController
from allura.lib import helpers as h
from allura.lib.security import has_access, require_access
from allura.lib.search import search, SolrError
from allura.lib.widgets.search import SearchResults
from allura.lib.decorators import require_post

# Local imports
from forgepastebin import version
from forgepastebin import widgets
from forgepastebin import model as PBM

log = logging.getLogger(__name__)

class ForgePastebin(Application):
    '''This is the Link app for PyForge'''
    __version__ = version.__version__
    permissions = [ 'configure', 'read', 'write', 'private' ]
    config_options = Application.config_options + [
        ConfigOption('private_by_default', bool, False, 'Private by Default')
    ]
    searchable=True
    tool_label='Pastebin'
    default_mount_label='Pastebin'
    default_mount_point='pastebin'
    status='beta'
    ordinal=1
    icons={
        24:'pastebin/images/pastebin_24.png',
        32:'pastebin/images/pastebin_32.png',
        48:'pastebin/images/pastebin_48.png'
    }

    def __init__(self, project, config):
        Application.__init__(self, project, config)
        self.root = RootController()
        self.admin = AdminController(self)

    @property
    @h.exceptionless([], log)
    def sitemap(self):
        menu_id = self.config.options.mount_label.title()
        return [SitemapEntry(menu_id, '.')[self.sidebar_menu()] ]

    def sidebar_menu(self):
        links = []
        if has_access(self, 'write')():
            links.append(SitemapEntry('New Paste',
                self.config.url() + 'new', ui_icon=g.icons['plus']))
        links.append(SitemapEntry('Recent Pastes',
            self.config.url()))
        return links

    def admin_menu(self):
        return super(ForgePastebin, self).admin_menu()

    def install(self, project):
        'Set up any default permissions and roles here'
        super(ForgePastebin, self).install(project)
        # Setup permissions
        role_anon = M.ProjectRole.anonymous()._id
        role_member = M.ProjectRole.by_name('Member')._id
        role_developer = M.ProjectRole.by_name('Developer')._id
        role_admin = M.ProjectRole.by_name('Admin')._id
        self.config.acl = [
            M.ACE.allow(role_anon, 'read'),
            M.ACE.allow(role_member, 'write'),
            M.ACE.allow(role_admin, 'configure'),
            M.ACE.allow(role_developer, 'private'),
            ]

    def uninstall(self, project):
        "Remove all the tool's artifacts from the database"
        super(ForgePastebin, self).uninstall(project)


class W:
    paste_form = widgets.PasteForm
    search_results = SearchResults()

class RootController(BaseController):
    def _check_security(self):
        require_access(c.app, 'read')

    @expose()
    def _lookup(self, paste_id, *remainder):
        return PasteController(paste_id), remainder

    @expose('jinja:forgepastebin:templates/new.html')
    def new(self, ref_id=None, **kw):
        require_access(c.app, 'write')
        allow_private = has_access(c.app, 'private')()
        c.paste_form = W.paste_form()
        ctx = dict(
                allow_private=allow_private,
                private=c.app.config.options.get('private_by_default', False),
            )
        if ref_id is not None:
            ref_paste = PBM.Paste.query.get(_id=ObjectId(ref_id))
            if ref_paste and (allow_private or not ref_paste.private):
                ctx['lang'] = ref_paste.lang
                ctx['text'] = ref_paste.text
                ctx['private'] = ref_paste.private
        return ctx

    @require_post()
    @expose()
    def create(self, text, lang, private=False, **kw):
        require_access(c.app, 'write')
        allow_private = has_access(c.app, 'private')()
        if not allow_private:
            private = False
        p = PBM.Paste(creator_id=c.user._id, text=text, lang=lang, private=asbool(private))
        redirect(p.url())

    @expose('jinja:forgepastebin:templates/pastes.html')
    def index(self, **kw):
        query = dict(deleted=False)
        if not has_access(c.app, 'private')():
            query['private'] = {'$in': [None, False]}
        pastes = PBM.Paste.query.find(query).sort('mod_date',
                pymongo.DESCENDING).limit(10).all()
        return dict(pastes=pastes)

    @with_trailing_slash
    @expose('jinja:forgepastebin:templates/pastes.html')
    def search(self, q, limit=None, page=0, **kwargs):
        search_error = None
        results = []
        count=0
        limit, page, start = g.handle_paging(limit, page, default=25)
        if not q:
            q = ''
        else:
            try:
                if not has_access(c.app, 'private')():
                    private = ['-is_private_b:true']
                else:
                    private = []
                results = search(
                    q, short_timeout=True, ignore_errors=False,
                    rows=limit, start=start,
                    fq=[
                        'project_id_s:%s' % c.project._id,
                        'mount_point_s:%s'% c.app.config.options.mount_point,
                        'type_s:Paste',
                        '-deleted_b:true'] + private)
            except SolrError as e:
                search_error = e
        if results:
            count=results.hits
        c.search_results = W.search_results
        pastes = (PBM.Paste.query.get(_id=ObjectId(r['id'][6:])) for r in results or [])
        return dict(q=q, pastes=pastes, title='Search Results',
                    count=count, limit=limit, page=page, search_error=search_error)

class PasteController(BaseController):
    def _check_security(self):
        if self.paste.private:
            require_access(c.app, 'private')
        else:
            require_access(c.app, 'read')

    def __init__(self, paste_id):
        if paste_id.endswith('.js'):
            paste_id, ext = paste_id.split('.')
        try:
            self.paste = PBM.Paste.query.get(_id=ObjectId(paste_id))
        except InvalidId as e:
            self.paste = None
        if self.paste is None:
            raise exc.HTTPNotFound()

    @without_trailing_slash
    @expose('jinja:forgepastebin:templates/paste/paste.js', content_type='text/javascript')
    @expose('jinja:forgepastebin:templates/paste/paste.html')
    def index(self, **kw):
        if self.paste.deleted:
            raise exc.HTTPNotFound()
        if request.path.endswith('.js'):
            request.response_type = 'text/javascript'
            csslink = ew.CSSLink('tool/%s/%s' % (c.app.config.tool_name.lower(), 'css/pygments.css'))
            g.resource_manager.register(csslink)
            css = urlparse.urljoin('//%s' % request.host, csslink.url())
            return dict(paste=json.dumps(self.paste.html()), js=True, csslink=json.dumps(css))
        else:
            is_admin = has_access(c.project, 'admin')()
            is_anon = c.user == M.User.anonymous()
            is_owner = not is_anon and c.user._id == self.paste.creator_id
            return dict(paste=self.paste, js=False, can_delete=is_owner or is_admin)

    @without_trailing_slash
    @expose()
    def delete(self, **kw):
        is_admin = has_access(c.project, 'admin')()
        is_anon = c.user == M.User.anonymous()
        is_owner = not is_anon and c.user._id == self.paste.creator_id
        if not (is_owner or is_admin):
            raise exc.HTTPForbidden()
        self.paste.deleted = True
        redirect('..')

class AdminController(DefaultAdminController):
    pass
