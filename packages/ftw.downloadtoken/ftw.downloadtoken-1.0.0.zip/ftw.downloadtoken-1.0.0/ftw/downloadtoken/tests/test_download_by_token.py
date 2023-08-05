from ftw.builder import Builder
from ftw.builder import create
from ftw.downloadtoken.interfaces import IDownloadTokenStorage
from ftw.downloadtoken.testing import FTW_DOWNLOADTOKEN_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from Products.CMFPlone.utils import getToolByName
from unittest2 import TestCase
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
import transaction


class TestStorage(TestCase):

    layer = FTW_DOWNLOADTOKEN_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.storage = IDownloadTokenStorage(self.portal)

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(('Folder',),
                                      ('plone_workflow',))

    @browsing
    def test_download_fails_if_not_token_given(self, browser):
        with self.assertRaises(BadRequest):
            browser.visit(view='download-token')

    @browsing
    def test_download_fails_invalid_token_given(self, browser):
        url = self.portal.portal_url() + '/download-token?token=12345'
        with self.assertRaises(BadRequest):
            browser.open(url)

    @browsing
    def test_download_file_by_token(self, browser):
        folder = create(Builder('folder').in_state('private'))
        file_ = create(Builder('file')
            .with_dummy_content()
            .within(folder))

        with self.assertRaises(Unauthorized):
            browser.visit(file_)

        downloadtoken = self.storage.add(file_, 'name@example.com')
        url = self.storage.url(downloadtoken)
        transaction.commit()

        browser.open(url)
        self.assertEquals('Test data', browser.contents)

    @browsing
    def test_download_fails_if_file_is_deleted(self, browser):
        folder = create(Builder('folder').in_state('private'))
        file_ = create(Builder('file')
            .with_dummy_content()
            .within(folder))

        downloadtoken = self.storage.add(file_, 'name@example.com')
        url = self.storage.url(downloadtoken)

        folder.manage_delObjects([file_.getId()])
        transaction.commit()

        with self.assertRaises(NotFound):
            browser.open(url)
