import logging
from urlparse import urlparse

from zope.component import getUtility
from zope.annotation import IAnnotations

from plone.registry.interfaces import IRegistry

from collective.slideshare.config import KEY, SLIDES_MIMETYPES
from collective.slideshare.interfaces import ISlideshareSettings
import collective.slideshare.utils

logger = logging.getLogger('collective.slideshare')

def get_slideshare_id(context, event):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISlideshareSettings)
    if not(settings.api_key and settings.shared_secret):
        return
    urlob = urlparse(context.getRemoteUrl())
    if urlob.hostname != 'www.slideshare.net':
        return
    annotations = IAnnotations(context)
    sl_id = annotations.get(KEY, None)
    if not(sl_id):
        msg = collective.slideshare.utils.get_slideshare_id(
            settings.api_key, settings.shared_secret, context)



def post_to_slideshare(context, event):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISlideshareSettings)
    if not(settings.api_key and settings.shared_secret and
                settings.username and settings.password and
                settings.push_on_publish and
                settings.user_policy != 'user' ):
        return
    if not(context.getContentType() in SLIDES_MIMETYPES):
        return
    if event.action == 'publish':
        annotations = IAnnotations(context)
        sl_id = annotations.get(KEY, None)
        if not(sl_id):
            msg = collective.slideshare.utils.post_to_slideshare(
                settings.api_key, settings.shared_secret,
                settings.username, settings.password,
                context)





