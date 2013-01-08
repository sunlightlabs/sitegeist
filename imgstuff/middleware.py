import logging

logger = logging.getLogger('imgstuff')


class ImgStuffMiddleware(object):

    def process_request(self, request):

        highres = request.GET.get('highres') == '1'
        request.highres = highres

        logger.debug("high res: %s" % highres)
