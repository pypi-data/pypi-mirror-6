class Tween(object):

    def __init__(self, handler, config):
        self.handler = handler
        self.text = config.get('versionbadge.text', 'BETA')
        self.css = config.get('versionbadge.css', '')

    def __call__(self, request):
        response = self.handler(request)
        if self.text != '' and (response.content_type and
                response.content_type.lower() in ['text/html',
                                                  'text/xml']):
            result = response.body
            result = result.replace('</body>',
                   '<div id="versionbadge" class="{}">{}</div></body>'.format(
                   self.css, self.text))
            response.body = ''
            response.write(result)
            return response
        return response


def factory(handler, registry):
    return Tween(handler, registry.settings.copy())


def includeme(config):
    config.add_tween('pyramid_versionbadge.factory')
