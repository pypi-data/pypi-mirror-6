from ftw.downloadtoken.interfaces import IDownloadTokenStorage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zExceptions import NotFound
import AccessControl


class SwitchedToSystemUser(object):
    """Switch temp. to System user
    """

    def __init__(self):
        self._original_security = None

    def __enter__(self):
        assert self._original_security is None

        self._original_security = AccessControl.getSecurityManager()

        _system_user = AccessControl.SecurityManagement.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(None, _system_user)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        AccessControl.SecurityManagement.setSecurityManager(
            self._original_security)
        self._original_security = None


class DownloadFile(BrowserView):
    def __call__(self):
        token = self.request.get('token', None)
        if token is None:
            raise BadRequest('No token')

        storage = IDownloadTokenStorage(self.context)
        downloadtoken = storage.get_downloadtoken(token)

        if downloadtoken is None:
            raise BadRequest('No valid token')

        return self.download_file(downloadtoken)

    def download_file(self, downloadtoken):
        catalog = getToolByName(self.context, 'portal_catalog')
        result = catalog.unrestrictedSearchResults(
            dict(UID=downloadtoken.uuid))

        if len(result) != 1:
            raise NotFound

        with SwitchedToSystemUser():
            obj = result[0].getObject()
            field = obj.getPrimaryField()
            return field.index_html(obj, disposition='attachment')
