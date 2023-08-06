# -*- coding: utf-8 -*-
from __future__ import with_statement
import datetime
import json
from cms.api import create_page, publish_page, add_plugin
from django.test import testcases
from django.core.management import call_command
from django.conf import settings
import os

class FileSystemPluginTests(testcases.TestCase):
    def setUp(self):
        super(FileSystemPluginTests, self).setUp()
        call_command('collectstatic', interactive=False, verbosity=0, link=True)

    def tearDown(self):
        for directory in [settings.STATIC_ROOT, settings.MEDIA_ROOT]:
            for root, dirs, files in os.walk(directory, topdown=False):
                # We need to walk() the directory tree since rmdir() does not allow
                # to remove non-empty directories...
                for name in files:
                    # Start by killing all files we walked
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    # Now all directories we walked...
                    os.rmdir(os.path.join(root, name))
        super(FileSystemPluginTests, self).tearDown()

    def test_fileplugin_icon_uppercase(self):
        page = create_page('testpage', 'dummy.html', 'en')
        body = page.placeholders.get(slot="body")
        plugin = File(
            plugin_type='FilePlugin',
            placeholder=body,
            position=1,
            language=settings.LANGUAGE_CODE,
        )
        plugin.file.save("UPPERCASE.JPG", SimpleUploadedFile("UPPERCASE.jpg", b"content"), False)
        plugin.insert_at(None, position='last-child', save=True)
        self.assertNotEquals(plugin.get_icon_url().find('jpg'), -1)
