from DateTime import DateTime
from ftw.downloadtoken import _
from ftw.downloadtoken.interfaces import IDownloadTokenStorage
from ftw.sendmail.composer import HTMLComposer
from plone import api
from z3c.form import button
from z3c.form import form
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.field import Fields
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
import re


class ISendMailSchema(Interface):
    """Send mail schema"""

    recipients = schema.List(
        value_type=schema.TextLine(),
        title=_(u'label_recipients', default=u'Recipients'),
        description=_(u'help_recipients',
                      default=u'One email address per line'),
        required=True)

    comment = schema.Text(
        title=_(u'label_comment', default=u'Comment'),
        required=False)

    @invariant
    def valid_email_addresses(data):
        expr = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=" +
                          r"?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?" +
                          r"\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
                          re.IGNORECASE)

        for mail in data.recipients:
            if not expr.match(mail):
                raise Invalid(_(u'text_error_invalid_email',
                                default=u'You entered one or more invalid '
                                         'email addresses.'))


class SendMailForm(form.Form):
    """Send mail form"""

    label = _(u'label_send_file', default=u'Send file')

    fields = Fields(ISendMailSchema)
    ignoreContext = True

    def updateWidgets(self):
        super(SendMailForm, self).updateWidgets()
        self.widgets['recipients'].widgetFactory = TextLinesWidget
        self.widgets['recipients'].rows = 8

    def updateActions(self):
        super(SendMailForm, self).updateActions()
        self.actions['label_send'].addClass("context")
        self.actions['label_cancel'].addClass("destructive")

    @button.buttonAndHandler(_(u"label_send", default="Send"))
    def send(self, action):
        data, errors = self.extractData()
        if errors:
            return
        self.send_mail(data)

        api.portal.show_message(
            message=_(u'text_send_mail',
                default='The given recipients has been notified.'),
            request=self.request,
            type='info')

        self.redirect()

    @button.buttonAndHandler(_(u"label_cancel", default="Cancel"))
    def cancel(self, action):
        self.redirect()

    def redirect(self):
        url = '{0}/view'.format(self.context.absolute_url())
        return self.request.RESPONSE.redirect(url)

    def send_mail(self, data):
        portal = api.portal.get()
        storage = IDownloadTokenStorage(portal)
        mail_template = self.context.restrictedTraverse('@@mail_downloadtoken')

        comment = data['comment']
        subject = translate(_(u'mail_subject',
                              default=u'[${title}] Download link',
                              mapping={'title': self.context.Title().decode(
                                  'utf-8')}),
                            context=self.request)

        for email in data['recipients']:
            downloadtoken = storage.add(self.context, email)

            options = {'user': api.user.get_current(),
                       'date': DateTime(),
                       'link': storage.url(downloadtoken),
                       'comment': comment}
            mail = mail_template(**options)

            composer = HTMLComposer(
                message=mail,
                subject=subject,
                to_addresses=[(email, email)])
            composed = composer.render()

            mh = api.portal.get_tool(name='MailHost')
            mh.send(composed.as_string(),
                    mto=composed['To'],
                    mfrom=composed['From'])
