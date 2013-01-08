import base64
import logging
import mimetypes
import os

from django import template
from django.contrib.staticfiles import storage

register = template.Library()
logger = logging.getLogger('imgstuff')


def local_path(path):
    local = storage.staticfiles_storage.path(path)
    logger.info("local path: %s -> %s" % (path, local))
    return local


def select_image(path, highres=False):
    """ Find the path to an image, high resolution if requested.
    """

    parts = path.split('/')

    if highres:

        parts[-1] = "%s@2x.%s" % tuple(parts[-1].rsplit('.', 1))
        path_hr = "/".join(parts)

        logger.info("highres path: %s" % path_hr)

        lp = local_path(path_hr)
        if lp and os.path.exists(lp):
            path = path_hr

    return path


@register.simple_tag(takes_context=True)
def img(context, path):
    """ Render a URL to the specificed image, using retina if it
        is requested and exists.
    """

    request = context['request']
    highres = getattr(request, 'highres', False)

    path = select_image(path, highres)

    logger.info("template path: %s" % path)

    return storage.staticfiles_storage.url(path)


@register.simple_tag(takes_context=True)
def inlineimg(context, path):
    """ Render an image inline using a data:// URI. Will return
        a retina version if it is requested and exists.
    """

    request = context['request']
    highres = getattr(request, 'highres', False)

    path = select_image(path, highres)
    content_type = mimetypes.guess_type(path)[0]

    lp = local_path(path)
    with open(lp) as infile:
        data = base64.b64encode(infile.read())

    uri = "data:%s;base64,%s" % (content_type, data)
    return uri
