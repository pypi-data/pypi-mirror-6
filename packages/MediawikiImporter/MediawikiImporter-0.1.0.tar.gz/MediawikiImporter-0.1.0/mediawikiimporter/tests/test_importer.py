from unittest import TestCase
from mock import Mock, patch
from ming.odm import ThreadLocalORMSession

from allura.tests import TestController
from allura.tests.decorators import with_wiki
from allura import model as M

from mediawikiimporter.importer import (
    MediawikiImporter,
    MediawikiImportController,
)


class TestMediawikiImporter(TestController, TestCase):

    @patch('mediawikiimporter.importer.AuditLog')
    @patch('mediawikiimporter.importer.g')
    @patch('mediawikiimporter.importer.argparse.Namespace')
    @patch('mediawikiimporter.importer.Wiki2Markdown')
    def test_import_tool(self, Wiki2Markdown, Namespace, g, AuditLog):
        importer = MediawikiImporter()
        app = Mock(name='ForgeWikiApp')
        app.config.options.mount_point = 'pages'
        app.url = 'foo'
        project = Mock(name='Project', shortname='myproject')
        project.install_app.return_value = app
        user = Mock(name='User', _id='id')
        res = importer.import_tool(project, user,
                mount_point='pages',
                mount_label='Pages',
                project_name='fancypants')
        self.assertEqual(res, app)
        project.install_app.assert_called_once_with(
                'Wiki', mount_point='pages', mount_label='Pages',
                import_id={
                        'source': 'Mediawiki',
                        'project_name': 'fancypants',
                    },
            )
        options = Namespace.return_value
        self.assertEqual(options.nbhd, project.neighborhood.name)
        self.assertEqual(options.project, 'myproject')
        self.assertEqual(options.mount_point, 'pages')
        self.assertEqual(options.db_config_prefix, 'hostedapps.db.')
        self.assertEqual(options.attachments_dir, '/nfs/mediawiki-attachments/f/fa/fancypants/')
        self.assertEqual(options.db_name, 'p_fancypants_mediawiki')
        self.assertEqual(options.extract, True)
        self.assertEqual(options.load, True)
        self.assertEqual(options.source, 'mysql')
        self.assertEqual(options.keep_dumps, False)
        Wiki2Markdown.execute.assert_called_once_with(Namespace.return_value)
        AuditLog.log.assert_called_once_with(
                'import tool pages from fancypants',
                project=project,
                user=user,
                url='foo',
        )
        g.post_event.assert_called_once_with('project_updated')

    @patch('mediawikiimporter.importer.Wiki2Markdown')
    @patch('mediawikiimporter.importer.h')
    def test_import_tool_failure(self, h, Wiki2Markdown):
        Wiki2Markdown.execute.side_effect = ValueError
        importer = MediawikiImporter()
        app = Mock(name='ForgeWikiApp')
        project = Mock(name='Project', shortname='myproject')
        project.install_app.return_value = app
        user = Mock(name='User', _id='id')
        self.assertRaises(ValueError, importer.import_tool,
                project, user,
                mount_point='pages',
                mount_label='Pages',
                project_name='fancypants')
        h.make_app_admin_only.assert_called_once_with(app)


class TestMediawikiImportController(TestController, TestCase):
    def setUp(self):
        """Mount Mediawiki import controller on the Wiki admin controller"""
        super(self.__class__, self).setUp()
        from forgewiki.wiki_main import WikiAdminController
        WikiAdminController._importer = \
                MediawikiImportController(MediawikiImporter())

    @with_wiki
    def test_index(self):
        r = self.app.get('/p/test/admin/wiki/_importer/')
        self.assertIsNotNone(r.html.find(attrs=dict(name="project_name")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_label")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_point")))

    @with_wiki
    @patch('forgeimporters.base.import_tool')
    def test_create(self, import_tool):
        params = dict(project_name='fancypants',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302)
        self.assertEqual(r.location, 'http://localhost/p/test/admin/')
        self.assertEqual(u'mymount', import_tool.post.call_args[1]['mount_point'])
        self.assertEqual(u'mylabel', import_tool.post.call_args[1]['mount_label'])
        self.assertEqual(u'fancypants', import_tool.post.call_args[1]['project_name'])

    @with_wiki
    @patch('forgeimporters.base.import_tool')
    def test_create_limit(self, import_tool):
        project = M.Project.query.get(shortname='test')
        project.set_tool_data('MediawikiImporter', pending=1)
        ThreadLocalORMSession.flush_all()
        params = dict(project_name='fancypants',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302).follow()
        self.assertIn('Please wait and try again', r)
        self.assertEqual(import_tool.post.call_count, 0)
