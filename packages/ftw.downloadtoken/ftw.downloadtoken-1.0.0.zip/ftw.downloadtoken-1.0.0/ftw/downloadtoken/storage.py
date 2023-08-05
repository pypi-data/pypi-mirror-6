from datetime import datetime, timedelta
from interfaces import IDownloadTokenStorage
from persistent import Persistent
from persistent.list import PersistentList
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements
import os


EXPIRATION_IN_DAYS = 7
DOWNLOAD_TOKEN_STORAGE_KEY = 'ftw.downloadtoken.storage'


class DownloadToken(Persistent):

    def __init__(self, token, uuid, email):
        self.token = token
        self.uuid = uuid
        self.email = email
        self.expiration_date = datetime.now() + timedelta(
            days=EXPIRATION_IN_DAYS)


class DownloadTokenStorage(object):

    implements(IDownloadTokenStorage)
    adapts(IPloneSiteRoot)

    def __init__(self, portal):
        self.context = portal

    def get_storage(self):
        annotations = IAnnotations(self.context)
        if DOWNLOAD_TOKEN_STORAGE_KEY not in annotations:
            annotations[DOWNLOAD_TOKEN_STORAGE_KEY] = PersistentList()
        return annotations[DOWNLOAD_TOKEN_STORAGE_KEY]

    def add(self, obj, email):
        token = os.urandom(32).encode('hex')
        new = DownloadToken(token=token,
                            uuid=IUUID(obj),
                            email=email)
        self.get_storage().append(new)
        self.cleanup()
        return new

    def remove(self, downloadtoken):
        self.get_storage().remove(downloadtoken)

    def get_downloadtoken(self, token):
        for downloadtoken in self.get_storage():
            if downloadtoken.token == token:
                return downloadtoken
        return None

    def url(self, downloadtoken):
        return '{0}/download-token?token={1}'.format(
            self.context.portal_url(), downloadtoken.token)

    def cleanup(self):
        for downloadtoken in tuple(self.get_storage()):
            if (datetime.now() - downloadtoken.expiration_date).days > 7:
                self.remove(downloadtoken)
