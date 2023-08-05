import logging

from zope.annotation import IAnnotations

from collective.slideshare.config import KEY
from collective.slideshare import slideshareMessageFactory as _

import slideshare


def post_to_slideshare(api_key, shared_secret, username, password, context):
    """ post a file to slideshare, annotate the object"""
    api = slideshare.SlideshareAPI(api_key, shared_secret)
    srcfile = dict(
        filehandle=context.getFile().getIterator(),
        filename=context.getFilename(),
        mimetype=context.getContentType()
        )
    try:
        sls = api.upload_slideshow(username, password,
            slideshow_title = context.Title(),
            slideshow_srcfile = srcfile,
            slideshow_description = context.Description(),
            slideshow_tags = ','.join(context.Subject()))
    except slideshare.SlideShareServiceError, exc:
        context.setLayout(context.getDefaultLayout())
        return str(exc)
    sl_id = sls['SlideShowUploaded']['SlideShowID']
    annotations = IAnnotations(context)
    annotations[KEY] = sl_id
    msg = _(u"Slideshow uploaded")
    if 'slideshare_view.html' in [l[0] for l in context.getAvailableLayouts()]:
        context.setLayout('slideshare_view.html')
    return msg

def get_slideshare_id(api_key, shared_secret, context):
    """From a link to a slideshare slideshow get the slideshareId
    and  annotate the object"""
    api = slideshare.SlideshareAPI(api_key, shared_secret)
    try:
        sls = api.get_slideshow(slideshow_url=context.getRemoteUrl())
    except slideshare.SlideShareServiceError, exc:
        context.setLayout(context.getDefaultLayout())
        return str(exc)
    title = sls['Slideshow'].get('Title')
    description = sls['Slideshow'].get('Description')
    #tags = sls['Slideshow'].get('Tags')
    sl_id = sls['Slideshow']['ID']
    annotations = IAnnotations(context)
    annotations[KEY] = sl_id
    if title and not context.Title():
        context.setTitle(title)
    if description and not context.Description():
        context.setDescription(description)

    msg = _(u"Slideshow embedded")
    if 'slideshare_view.html' in [l[0] for l in context.getAvailableLayouts()]:
        context.setLayout('slideshare_view.html')
    return msg



