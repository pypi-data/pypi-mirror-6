from five import grok
from Products.CMFCore.interfaces import IContentish
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import json
from plone.z3cform.z2 import processInputs
from z3c.form import form
from zope.interface import Interface
from zope import schema
from z3c.form import field
from z3c.form import button
from plone.z3cform import layout
from Products.CMFPlone.utils import safe_unicode
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email import Encoders
from collective.pdfexport.interfaces import IPDFConverter
from Products.statusmessages.interfaces import IStatusMessage
import json
from plone import api
from zope.component.hooks import getSite
from zope.component import getAdapters
from collective.pdfexport.interfaces import IPDFEmailSource

grok.templatedir('templates')

class SendAsPDF(grok.View):
    grok.context(IContentish)
    grok.name('send_as_pdf')
    grok.template('send_as_pdf')

    label = u'Send this page as PDF'

    def js(self):

        config = {
            'theme': 'facebook',
            'tokenDelimiter': '\n',
            'preventDuplicates': True,
        }

        if self.defaults['sendaspdf-recipients']:
            config['prePopulate'] = [{
                'id': i, 'name': i
            } for i in self.defaults['sendaspdf-recipients'].splitlines()]

        return '''
            $(document).ready(function () {
                $('#sendaspdf-recipients').tokenInput('%s', %s);
            })
        ''' % (
            self.context.absolute_url() + '/sendaspdf-recipients',
            json.dumps(config)
        )

    def update(self):
        if self.request.method != 'POST':
            self.defaults = {
                'sendaspdf-recipients':'',
                'sendaspdf-subject': '',
                'sendaspdf-message': ''
            } 
            return
          
        recipients = self.request.get('sendaspdf-recipients', '').strip()
        subject = self.request.get('sendaspdf-subject', '').strip()
        message = self.request.get('sendaspdf-message', '').strip()
        self.defaults = {
            'sendaspdf-recipients': recipients,
            'sendaspdf-subject': subject,
            'sendaspdf-message': message
        }
        statusmessages = IStatusMessage(self.request)
        if not subject:
            statusmessages.add('Subject is required', type='error')
        if not recipients:
            statusmessages.add('Recipients is required', type='error')
        if not message:
            statusmessages.add('Message is required', type='error')
        if not (subject and recipients and message):
            return

        expanded_recipients = []
        adapters = getAdapters((self.context,), IPDFEmailSource)
        for recipient in recipients.splitlines():
            expanded = False
            for name, adapter in adapters:
                if adapter.can_expand(recipient):
                    expanded_recipients += adapter.expand_value(recipient)
                    expanded = True
                    break
            if not expanded:
                expanded_recipients.append(recipient)

        self.send_email(
            recipients=list(set(expanded_recipients)),
            subject=subject,
            message=message
        )

        statusmessages.add('Emails sent')
        self.request.response.redirect(self.context.absolute_url())

    def send_email(self, recipients, subject, message):
        mailhost = self.context.MailHost
        
        from_address = api.user.get_current().getProperty('email')

        if not from_address:
            from_address = self.context.email_from_address
        
        from_name = api.user.get_current().getProperty('fullname')

        if not from_name:
            from_name = self.context.email_from_name

        source = '%s <%s>' % (from_name, from_address)

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = source
        
        body = u'''
You are receiving this mail because someone read a page at %(sitename)s and 
thought it might interest you.

It is sent by %(sender)s with the following comment:

"%(message)s"

See the attachment for the page.
        ''' % {
            'sitename': getSite().title,
            'sender': from_name,
            'message': message
        }
        htmlPart = MIMEText(body, 'plain', 'utf-8')
        msg.attach(htmlPart)

        converter = getUtility(IPDFConverter)
        view = self.request.get('pdf-view', None)
        pdf = converter.convert(self.context, view=view)

        attachment = MIMEBase('application', 'pdf')
        attachment.set_payload(pdf.buf)
        Encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment',
                          filename=self.context.Title() + '.pdf')
        msg.attach(attachment)

        for recipient in recipients:
            # skip broken recipients
            if not recipient:
                continue
            if '@' not in recipient:
                continue

            del msg['To']
            msg['To'] = recipient
            mailhost.send(msg.as_string())
     

         
            
class Recipients(grok.View):
    grok.context(IContentish)
    grok.name('sendaspdf-recipients')

    def render(self):
        self.request.response.setHeader("Content-type", "application/json")
        adapters = getAdapters((self.context,), IPDFEmailSource)

        keys = []
        if 'q' in self.request.keys():
            q = self.request['q']
            for name, adapter in adapters:
                keys += adapter.search(q)

        # we will return up to 10 tokens only
        tokens = map(self._tokenize, keys[:10])
        return json.dumps(tokens)

    def _tokenize(self, key):
        value = key['value'].decode('utf-8')
        title = key['title'].decode('utf-8')

        return {'id': '%s' % value.replace(u"'", u"\\'"),
                'name': '%s' % title.replace(u"'", u"\\'")}

class SendThis(grok.View):
    grok.context(IContentish)
    grok.name('sendthis_form')
    grok.template('send_as_pdf')

    label = u'Send this page'

    def js(self):

        config = {
            'theme': 'facebook',
            'tokenDelimiter': '\n',
            'preventDuplicates': True,
        }

        if self.defaults['sendaspdf-recipients']:
            config['prePopulate'] = [{
                'id': i, 'name': i
            } for i in self.defaults['sendaspdf-recipients'].splitlines()]

        return '''
            $(document).ready(function () {
                $('#sendaspdf-recipients').tokenInput('%s', %s);
            })
        ''' % (
            self.context.absolute_url() + '/sendaspdf-recipients',
            json.dumps(config)
        )

    def update(self):
        if self.request.method != 'POST':
            self.defaults = {
                'sendaspdf-recipients':'',
                'sendaspdf-subject': '',
                'sendaspdf-message': ''
            } 
            return
          
        recipients = self.request.get('sendaspdf-recipients', '').strip()
        subject = self.request.get('sendaspdf-subject', '').strip()
        message = self.request.get('sendaspdf-message', '').strip()
        self.defaults = {
            'sendaspdf-recipients': recipients,
            'sendaspdf-subject': subject,
            'sendaspdf-message': message
        }
        statusmessages = IStatusMessage(self.request)
        if not subject:
            statusmessages.add('Subject is required', type='error')
        if not recipients:
            statusmessages.add('Recipients is required', type='error')
        if not message:
            statusmessages.add('Message is required', type='error')
        if not (subject and recipients and message):
            return

        expanded_recipients = []
        adapters = getAdapters((self.context,), IPDFEmailSource)
        for recipient in recipients.splitlines():
            expanded = False
            for name, adapter in adapters:
                if adapter.can_expand(recipient):
                    expanded_recipients += adapter.expand_value(recipient)
                    expanded = True
                    break
            if not expanded:
                expanded_recipients.append(recipient)

        self.send_email(
            recipients=list(set(expanded_recipients)),
            subject=subject,
            message=message
        )

        statusmessages.add('Emails sent')
        self.request.response.redirect(self.context.absolute_url())

    def send_email(self, recipients, subject, message):
        mailhost = self.context.MailHost
        
        from_address = api.user.get_current().getProperty('email')

        if not from_address:
            from_address = self.context.email_from_address
        
        from_name = api.user.get_current().getProperty('fullname')

        if not from_name:
            from_name = self.context.email_from_name

        source = '%s <%s>' % (from_name, from_address)

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = source
        
        body = u'''
You are receiving this mail because someone read a page at %(sitename)s and 
thought it might interest you.

It is sent by %(sender)s with the following comment:

"%(message)s"

%(url)s
        ''' % {
            'sitename': getSite().title,
            'sender': from_name,
            'message': message,
            'url':self.context.absolute_url()
        }
        htmlPart = MIMEText(body, 'plain', 'utf-8')
        msg.attach(htmlPart)

        for recipient in recipients:
            # skip broken recipients
            if not recipient:
                continue
            if '@' not in recipient:
                continue

            del msg['To']
            msg['To'] = recipient
            mailhost.send(msg.as_string())
 
