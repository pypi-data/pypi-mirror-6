from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.downloadtoken.interfaces import IDownloadTokenStorage
from ftw.downloadtoken.storage import DownloadToken
from ftw.downloadtoken.testing import FTW_DOWNLOADTOKEN_INTEGRATION_TESTING
from persistent.list import PersistentList
from unittest2 import TestCase
from zope.interface.verify import verifyClass


class TestDownloadToken(TestCase):

    def test_download_token_init(self):
        new = DownloadToken(token='token',
                            uuid='uuid',
                            email='name@example.com')
        self.assertEquals('token', new.token)
        self.assertEquals('uuid', new.uuid)
        self.assertEquals('name@example.com', new.email)

    def test_download_token_expiration_date(self):
        new = DownloadToken(token='token',
                            uuid='uuid',
                            email='name@example.com')

        # 6 days, because some time is elapsed since method call.
        self.assertEquals(6,
                          (new.expiration_date - datetime.now()).days,
                          'datetime delta should be 6 days')


class TestStorage(TestCase):

    layer = FTW_DOWNLOADTOKEN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_implements_interface(self):
        storage = IDownloadTokenStorage(self.portal)
        verifyClass(IDownloadTokenStorage, storage.__class__)

    def test_initialize_storage(self):
        storage = IDownloadTokenStorage(self.portal)

        self.assertTrue(isinstance(storage.get_storage(), PersistentList),
                        'It has to be something persistent.')

    def test_extend_strorage(self):
        storage = IDownloadTokenStorage(self.portal)

        storage.get_storage().append('data')
        self.assertEquals(1, len(storage.get_storage()))

    def test_add_new_item_to_storage(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))

        added = storage.add(file_, 'name@example.com')

        self.assertEquals(1,
                          len(storage.get_storage()),
                          'Expect one item in storage')
        self.assertTrue(
            isinstance(storage.get_storage()[0], DownloadToken),
            'Item is not a DownloadToken instance.')
        self.assertEquals(added, storage.get_storage()[0])

    def test_remove_item_from_storage(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))

        added = storage.add(file_, 'name@example.com')
        storage.remove(added)

        self.assertFalse(len(storage.get_storage()),
                         'Storage should be empty.')

    def test_get_downloadtoken_by_token(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))

        added = storage.add(file_, 'name@example.com')
        self.assertEquals(added, storage.get_downloadtoken(added.token))

    def test_get_inexistend_downloadtoken(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))

        storage.add(file_, 'name@example.com')
        self.assertIsNone(storage.get_downloadtoken('12345'))

    def test_downloadtoken_url(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))

        added = storage.add(file_, 'name@example.com')

        url = '{0}/download-token?token={1}'.format(
            self.portal.portal_url(),
            added.token)

        self.assertEquals(url, storage.url(added))

    def test_storage_cleanup(self):
        storage = IDownloadTokenStorage(self.portal)
        file_ = create(Builder('file'))
        expiredtoken1 = storage.add(file_, 'email@example.com')
        expiredtoken2 = storage.add(file_, 'email@example.com')

        expiredtoken1.expiration_date = datetime.now() - timedelta(days=10)
        expiredtoken2.expiration_date = datetime.now() - timedelta(days=20)

        self.assertEquals(2,
                          len(storage.get_storage()),
                          'Expect two items')

        validtoken = storage.add(file_, 'email@new.com')

        self.assertEquals(1,
                          len(storage.get_storage()),
                          'Expect only the last added item. The others are '
                          'expired and removed.')
        self.assertEquals(validtoken.token,
                          storage.get_storage()[0].token,
                          'Found the wrong token.')
