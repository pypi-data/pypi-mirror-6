# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope import component

from ..testing import FunctionalLayer
from ..interfaces import ISitemapService

from silva.core.interfaces import IAccessSecurity


class ExcludedContentTestCase(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.service = component.getUtility(ISitemapService)
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('public', 'Public')
        factory.manage_addFolder('private', 'Private')

    def test_excluded_folder(self):
        private_path = self.root.private.getPhysicalPath()
        public_path = self.root.public.getPhysicalPath()

        self.assertFalse(self.service.is_path_excluded(public_path))
        self.assertFalse(self.service.is_path_excluded(private_path))
        self.assertFalse(self.service.is_path_excluded(
            private_path + ('subcomponent',)))
        self.assertFalse(self.service.is_path_excluded(
            self.root.getPhysicalPath()))

        self.service.exclude_content(self.root.private)
        self.assertFalse(self.service.is_path_excluded(
            self.root.getPhysicalPath()))
        self.assertFalse(self.service.is_path_excluded(public_path))
        self.assertTrue(self.service.is_path_excluded(
            private_path))
        self.assertTrue(self.service.is_path_excluded(
            private_path + ('subcomponent',)))

        self.service.unexclude_content(self.root.private)
        self.assertFalse(self.service.is_path_excluded(
            private_path))
        self.assertFalse(self.service.is_path_excluded(
            private_path + ('subcomponent',)))
        self.assertFalse(self.service.is_path_excluded(
            self.root.getPhysicalPath()))

    def test_container_excluded_when_rescriction_set(self):
        private_path = self.root.private.getPhysicalPath()
        self.assertFalse(self.service.is_path_excluded(private_path))
        IAccessSecurity(self.root.private).set_minimum_role('Authenticated')
        self.assertTrue(self.service.is_path_excluded(private_path))
        self.assertTrue(self.service.is_path_excluded(
            private_path + ('subcomponent',)))

        IAccessSecurity(self.root.private).set_minimum_role('Anonymous')
        self.assertFalse(self.service.is_path_excluded(private_path))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExcludedContentTestCase))
    return suite
