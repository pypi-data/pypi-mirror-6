import argparse
from datetime import (
        datetime,
        timedelta,
        )
import tempfile

from formencode import validators as fev
from ming.orm import session
from pylons import tmpl_context as c
from pylons import app_globals as g
from tg import (
        config,
        expose,
        flash,
        redirect,
        )
from tg.decorators import (
        with_trailing_slash,
        without_trailing_slash,
        )

from allura.lib.decorators import require_post
from allura.lib import helpers as h
from allura.model import ApiTicket, AuditLog

from forgeimporters.base import (
    ToolImporter,
    ToolImportForm,
    ToolImportController,
)
from forgeimporters.trac import TracURLValidator

from tracwikiimporter.scripts.wiki_from_trac.extractors import WikiExporter
from tracwikiimporter.scripts.wiki_from_trac.loaders import load_data
from tracwikiimporter.scripts.wiki_from_trac.wiki_from_trac import WikiFromTrac


class TracWikiImportForm(ToolImportForm):
    trac_url = TracURLValidator()


class TracWikiImportController(ToolImportController):
    import_form = TracWikiImportForm

    @with_trailing_slash
    @expose('jinja:tracwikiimporter:templates/index.html')
    def index(self, **kw):
        return dict(importer=self.importer,
                target_app=self.target_app)

    @without_trailing_slash
    @expose()
    @require_post()
    def create(self, trac_url, mount_point, mount_label, **kw):
        if self.importer.enforce_limit(c.project):
            self.importer.post(
                    mount_point=mount_point,
                    mount_label=mount_label,
                    trac_url=trac_url,
                    )
            flash('Wiki import has begun. Your new wiki will be available '
                    'when the import is complete.')
        else:
            flash('There are too many imports pending at this time.  Please wait and try again.', 'error')
        redirect(c.project.url() + 'admin/')


class TracWikiImporter(ToolImporter):
    target_app_ep_names = 'wiki'
    source = 'Trac'
    controller = TracWikiImportController
    tool_label = 'Wiki'
    tool_description = 'Import your wiki from Trac.  Note: wiki content is imported, but not revision history or attachments.'

    def import_tool(self, project, user, project_name=None, mount_point=None,
            mount_label=None, trac_url=None, **kw):
        """ Import Trac wiki into a new Allura Wiki tool.

        """
        mount_point = mount_point or 'wiki'
        app = project.install_app(
                'Wiki',
                mount_point=mount_point,
                mount_label=mount_label or 'Wiki',
                import_id={
                        'source': self.source,
                        'trac_url': trac_url,
                    },
            )
        session(app.config).flush(app.config)
        try:
            api_ticket = ApiTicket(user_id=user._id,
                    capabilities={"import": ["Projects", project.shortname]},
                    expires=datetime.utcnow() + timedelta(minutes=60))
            session(api_ticket).flush(api_ticket)
            options = argparse.Namespace()
            options.api_key = api_ticket.api_key
            options.secret_key = api_ticket.secret_key
            options.wiki = mount_point
            options.base_url = config['base_url']
            options.verbose = False
            options.converter = 'html2text'
            options.import_opts = []
            options.user_map_file = None
            options.neighborhood, options.project = project.url().strip('/').split('/',1)
            with tempfile.NamedTemporaryFile() as f:
                WikiExporter(trac_url, options).export(f)
                f.flush()
                load_data(f.name, WikiFromTrac.parser(), options)
            AuditLog.log('import tool %s from %s' %
                    (app.config.options.mount_point, trac_url),
                    project=project, user=user, url=app.url)
            g.post_event('project_updated')
            return app
        except Exception as e:
            h.make_app_admin_only(app)
            raise
