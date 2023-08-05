from ftw.builder import Builder
from ftw.builder import create
from ftw.downloadtoken.interfaces import IDownloadTokenStorage
from ftw.downloadtoken.testing import FTW_DOWNLOADTOKEN_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing.mailing import Mailing
from Products.CMFPlone.utils import getToolByName
from unittest2 import TestCase
from zExceptions import Unauthorized
import quopri
import re
import transaction


def get_link_from_email(mail):
    message = quopri.decodestring(mail)
    url = re.findall(r'(https?://\S+)', message)[1]
    return url


class TestStorage(TestCase):

    layer = FTW_DOWNLOADTOKEN_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.mails = Mailing(self.portal)
        self.mails.set_up()

        self.storage = IDownloadTokenStorage(self.portal)

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(('Folder',),
                                      ('plone_workflow',))
        transaction.commit()

        folder = create(Builder('folder').in_state('private'))
        self.file_ = create(Builder('file')
            .titled('\xc3\xa4 file')
            .with_dummy_content()
            .within(folder))

    def tearDown(self):
        Mailing(self.layer['portal']).tear_down()

    @browsing
    def test_send_mail_form(self, browser):
        browser.login().visit(self.file_, view='send-mail-form')
        browser.fill({'Recipients': 'email@example.com'})
        browser.find('Send').click()

        self.assertEquals(1,
                          len(self.mails.get_messages()),
                          'Expect one message')

        self.assertEquals('{0}/view'.format(self.file_.absolute_url()),
                          browser.url)

    @browsing
    def test_cancel_send_mail_form(self, browser):
        browser.login().visit(self.file_, view='send-mail-form')
        browser.find('Cancel').click()

        self.assertEquals(0,
                          len(self.mails.get_messages()),
                          'Expect one message')

        self.assertEquals('{0}/view'.format(self.file_.absolute_url()),
                          browser.url)

    @browsing
    def test_link_in_mail(self, browser):
        browser.login().visit(self.file_, view='send-mail-form')
        browser.fill({'Recipients': 'email@example.com'})
        browser.find('Send').click()

        mail = self.mails.pop()
        url = get_link_from_email(mail)
        browser.logout().open(url)

        with self.assertRaises(Unauthorized):
            browser.visit(self.file_)

        self.assertEquals('Test data', browser.contents)

    @browsing
    def test_multiple_recipients(self, browser):
        browser.login().visit(self.file_, view='send-mail-form')
        browser.fill({'Recipients': 'email@example.com\nemail2@example.com'})
        browser.find('Send').click()

        self.assertEquals(2,
                          len(self.mails.get_messages()),
                          'Expect two messages')

        self.assertEquals(2,
                          len(self.storage.get_storage()),
                          'Expect two items')

    @browsing
    def test_send_mail_form_valid_email_addresses(self, browser):
        browser.login().visit(self.file_, view='send-mail-form')
        browser.fill({'Recipients': 'email@example\n@example.com'})
        browser.find('Send').click()

        statusmessages.error_messages()
        self.assertFalse(len(self.storage.get_storage()), 'Expect no tokens.')

        browser.fill({'Recipients': u'em\xe4il@example'})
        statusmessages.error_messages()
