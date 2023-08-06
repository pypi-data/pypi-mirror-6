import argparse
import tempfile
import shutil

from formencode import validators as fev
from ming.orm import ThreadLocalORMSession
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
from allura.model import AuditLog

from forgeimporters.base import (
    ToolImporter,
    ToolImportForm,
    ToolImportController,
)

from mediawikiimporter.wiki2markdown import Wiki2Markdown


class MediawikiImportForm(ToolImportForm):
    project_name = fev.UnicodeString(not_empty=True)


class MediawikiImportController(ToolImportController):
    import_form = MediawikiImportForm

    @with_trailing_slash
    @expose('jinja:mediawikiimporter:templates/index.html')
    def index(self, **kw):
        return dict(importer=self.importer, target_app=self.target_app)

    @without_trailing_slash
    @expose()
    @require_post()
    def create(self, project_name, mount_point, mount_label, **kw):
        if self.importer.enforce_limit(c.project):
            self.importer.post(
                    mount_point=mount_point,
                    mount_label=mount_label,
                    project_name=project_name)
            flash('Wiki import has begun. Your new wiki will be available '
                                'when the import is complete.')
        else:
            flash('There are too many imports pending at this time.  Please wait and try again.', 'error')
        redirect(c.project.url() + 'admin/')


class MediawikiImporter(ToolImporter):
    target_app_ep_names = 'wiki'
    controller = MediawikiImportController
    tool_label = 'Wiki'
    tool_description = 'Import your mediawiki.'

    @property
    def source(self):
        return config['site_name'] + ' Mediawiki'

    def import_tool(self, project, user, project_name=None, mount_point='wiki',
                    mount_label='Wiki', **kw):
        app = project.install_app(
                'Wiki',
                mount_point=mount_point,
                mount_label=mount_label,
                import_id={'source': self.source, 'project_name': project_name}
        )
        ThreadLocalORMSession.flush_all()
        try:
            dump_dir = tempfile.mkdtemp()
            options = argparse.Namespace()
            options.nbhd = project.neighborhood.name
            options.project = project.shortname
            options.mount_point = mount_point
            options.db_config_prefix = config['mediawikiimporter.db_config_prefix']
            options.attachments_dir = '%s/%s/%s/%s/' % (
                config['mediawikiimporter.attachments_dir_prefix'].rstrip('/'),
                project_name[:1],
                project_name[:2],
                project_name,
            )
            options.db_name = config['mediawikiimporter.db_name_template'] % project_name
            options.dump_dir = dump_dir
            options.extract = True
            options.load = True
            options.source = 'mysql'
            options.keep_dumps = False
            Wiki2Markdown.execute(options)
            AuditLog.log('import tool %s from %s' %
                    (app.config.options.mount_point, project_name),
                    project=project, user=user, url=app.url)
            g.post_event('project_updated')
            return app
        except Exception:
            h.make_app_admin_only(app)
            raise
        finally:
            shutil.rmtree(dump_dir, ignore_errors=True)
