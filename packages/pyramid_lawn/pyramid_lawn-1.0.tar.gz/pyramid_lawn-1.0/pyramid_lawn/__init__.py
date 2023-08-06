import sys

from pyramid.authentication import AuthTktCookieHelper
from pyramid.httpexceptions import HTTPFound
from pyramid.paster import bootstrap
from pyramid.response import Response


TEN_YEARS = 10 * 365 * 24 * 60 * 60
IDENTITY = 'Let me in grumpy pants'


def get_off_my_lawn_tween_factory(handler, registry):
    def get_off_my_lawn(request):
        return Response("Get off my lawn!")

    secret = registry.settings.get('lawn_secret')
    if secret is None:
        return get_off_my_lawn

    def get_off_my_lawn_unless_you_know_the_secret_handshake(request):
        helper = AuthTktCookieHelper(secret, 'lawn', max_age=TEN_YEARS)
        identity = helper.identify(request)
        if not identity:
            trythisone = request.copy()
            trythisone.cookies['lawn'] = trythisone.path_info.strip('/')
            identity = helper.identify(trythisone)
            if identity:
                response = HTTPFound(request.application_url)
                response.headers.extend(helper.remember(request, IDENTITY))
                return response

        if identity and identity['userid'] == IDENTITY:
            return handler(request)

        return get_off_my_lawn(request)

    return get_off_my_lawn_unless_you_know_the_secret_handshake


def includeme(config):
    config.add_tween('pyramid_lawn.get_off_my_lawn_tween_factory')


def cli_gen_ticket():
    env = bootstrap(sys.argv[1])
    secret = env['registry'].settings.get('lawn_secret')
    if not secret:
        print "No secret configured."
        return
    helper = AuthTktCookieHelper(secret, 'lawn')
    cookie_value = helper.remember(env['request'], IDENTITY)[0][1]
    assert cookie_value.startswith('lawn="')
    print cookie_value.split(';')[0][6:-1]
