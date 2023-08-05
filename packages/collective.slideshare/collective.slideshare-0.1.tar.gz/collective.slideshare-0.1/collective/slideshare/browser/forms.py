import logging
from cStringIO import StringIO

from zope import interface, schema
from zope.formlib import form
from zope.formlib.textwidgets import PasswordWidget
from zope.component import getUtility
from zope.annotation import IAnnotations

from five.formlib import formbase

from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage

import slideshare

from collective.slideshare import slideshareMessageFactory as _
from collective.slideshare.interfaces import IPostToSlideshareSchema
from collective.slideshare.interfaces import ISlideshareSettings
from collective.slideshare.interfaces import IGetSlideshareIdSchema
from collective.slideshare.config import KEY
import collective.slideshare.utils

logger = logging.getLogger('collective.slideshare')

class PostToSlideshare(formbase.PageForm):
    form_fields = form.FormFields(IPostToSlideshareSchema)
    form_fields['password'].custom_widget = PasswordWidget
    label = _(u'Post to Slideshare')
    description = _(u'Supply your Slideshare credentials to upload')

    def __init__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISlideshareSettings)
        if self.settings.user_policy == "fixed":
            self.description = ""
            self.form_fields = self.form_fields.omit('username', 'password')
        elif self.settings.user_policy == "user":
            un = self.form_fields.get('username')
            un.field.required = True
            pw = self.form_fields.get('password')
            pw.field.required = True
        elif self.settings.user_policy == "optional":
            self.description = _(u"""Supply your Slideshare credentials
            if you want to upload the presentation to your own account.
            Your credentials will not be stored""")
            un = self.form_fields.get('username')
            un.field.required = False
            pw = self.form_fields.get('password')
            pw.field.required = False
        super(PostToSlideshare, self).__init__(*args, **kwargs)

    @property
    def next_url(self):
        url = self.context.absolute_url()
        url += '/view'
        return url

    @form.action('Submit')
    def actionSubmit(self, action, data):
        url = self.context.absolute_url()
        if self.settings.api_key and self.settings.shared_secret:
            api = slideshare.SlideshareAPI(self.settings.api_key,
                self.settings.shared_secret)
        else:
            msg = _(u"Slideshare API_KEY or SHARED_SECRET missing")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            self.request.response.redirect(self.next_url)
            return
        if self.settings.user_policy == "fixed":
            username = self.settings.username
            password = self.settings.password
        elif self.settings.user_policy == "user":
            username = data.get('username')
            password = data.get('password')
        elif self.settings.user_policy == "optional":
            username = data.get('username')
            password = data.get('password')
            if not(username and password):
                username = self.settings.username
                password = self.settings.password
        else:
            username = None
            password = None
        if not(username and password):
            msg = _(u"Slideshare USERNAME or PASSWORD missing")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return
        msg = collective.slideshare.utils.post_to_slideshare(
                self.settings.api_key, self.settings.shared_secret,
                username, password, self.context)
        self.request.response.redirect(self.next_url)
        msgtype = 'info'
        if 'SlideShareServiceError' in msg:
            msgtype = 'error'
        IStatusMessage(self.request).addStatusMessage(msg, type=msgtype)

    @form.action('Cancel')
    def actionCancel(self, action, data):
        if self.context.getLayout() == 'slideshare_view.html':
            self.context.setLayout(self.context.getDefaultLayout())
        self.request.response.redirect(self.next_url)

class GetSlideshareId(formbase.PageForm):
    form_fields = form.FormFields(IGetSlideshareIdSchema)
    label = _(u'Get embed information from Slideshare')
    description = _(u'Get the code to embed the slideshow from slideshare')

    def __init__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISlideshareSettings)
        super(GetSlideshareId, self).__init__(*args, **kwargs)

    @property
    def next_url(self):
        url = self.context.absolute_url()
        url += '/view'
        return url

    @form.action('Submit')
    def actionSubmit(self, action, data):
        if self.settings.api_key and self.settings.shared_secret:
            api = slideshare.SlideshareAPI(self.settings.api_key,
                self.settings.shared_secret)
        else:
            msg = _(u"Slideshare API_KEY or SHARED_SECRET missing")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            self.request.response.redirect(self.next_url)
            return
        msg = collective.slideshare.utils.get_slideshare_id(
            self.settings.api_key, self.settings.shared_secret,
            self.context)
        self.request.response.redirect(self.next_url)
        msgtype = 'info'
        if 'SlideShareServiceError' in msg:
            msgtype = 'error'
        IStatusMessage(self.request).addStatusMessage(msg, type=msgtype)

    @form.action('Cancel')
    def actionCancel(self, action, data):
        if self.context.getLayout() == 'slideshare_view.html':
            self.context.setLayout(self.context.getDefaultLayout())
        self.request.response.redirect(self.next_url)

class RemoveSlideshareId(formbase.PageForm):
    form_fields = form.FormFields(IGetSlideshareIdSchema)
    label = _(u'Remove the Slideshare id from content')
    description = _(u'If the slideshow was deleted from slideshare you can remove the id')

    @property
    def next_url(self):
        url = self.context.absolute_url()
        url += '/view'
        return url

    @form.action('Remove')
    def actionSubmit(self, action, data):
        annotations = IAnnotations(self.context)
        if annotations.get(KEY):
            annotations[KEY] = None
            msg = _(u"Slideshare id removed")
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
        else:
            msg = _(u"object does not have a slideshare id")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
        self.context.setLayout(self.context.getDefaultLayout())
        self.request.response.redirect(self.next_url)

    @form.action('Cancel')
    def actionCancel(self, action, data):
        self.request.response.redirect(self.next_url)
