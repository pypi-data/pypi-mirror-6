from urlparse import urlparse
from zope.interface import implements, Interface
from zope.annotation import IAnnotations
from zope.component import getUtility

from Products.Five import BrowserView
from Products.ATContentTypes.interfaces import IATLink, IATFile
from plone.registry.interfaces import IRegistry

from collective.slideshare.config import KEY, SLIDES_MIMETYPES
from collective.slideshare.interfaces import ISlideshareSettings
from collective.slideshare import slideshareMessageFactory as _

class ISlideshareView(Interface):
    """
    slideshare view interface
    """

class SlideshareView(BrowserView):
    """
    Display slideshare embeded file
    """
    implements(ISlideshareView)

    def __init__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISlideshareSettings)
        super(SlideshareView, self).__init__(*args, **kwargs)

    def get_url(self):
        if IATFile.providedBy(self.context):
            return self.context.absolute_url()
        elif IATLink.providedBy(self.context):
            return self.context.getRemoteUrl()

    def link_text(self):
        if IATFile.providedBy(self.context):
            return _("Download")
        elif IATLink.providedBy(self.context):
            return _("View it on SlideShare")


    def get_slid(self):
        """slideshare slideshowid or redirect to upload"""
        annotations = IAnnotations(self.context)
        sl_id = annotations.get(KEY, None)
        if sl_id:
            return sl_id
        else:
            if IATFile.providedBy(self.context):
                if self.context.getContentType() in SLIDES_MIMETYPES:
                    self.request.response.redirect(
                        self.context.absolute_url() +
                                '/@@slideshare_post.html')
                else:
                    msg = _(u"This file does not seem to be a presentation")
                    IStatusMessage(self.request).addStatusMessage(msg,
                            type='error')
            elif IATLink.providedBy(self.context):
                urlob = urlparse(self.context.getRemoteUrl())
                if urlob.hostname == 'www.slideshare.net':
                     self.request.response.redirect(
                        self.context.absolute_url() +
                                '/@@slideshare_getid.html')
                else:
                    msg = _(u"This is not a valid slideshare URL")
                    IStatusMessage(self.request).addStatusMessage(msg,
                            type='error')


    def get_height(self):
        return self.settings.height

    def get_width(self):
        return self.settings.width
