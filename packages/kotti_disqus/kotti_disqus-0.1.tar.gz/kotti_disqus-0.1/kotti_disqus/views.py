# -*- coding: utf-8 -*-

from kotti import get_settings
from kotti.views.slots import assign_slot
from kotti.views.util import template_api
from kotti_settings.util import get_settings as get_settings_util
from pyramid.exceptions import PredicateMismatch
from pyramid.util import DottedNameResolver
from pyramid.view import view_config


@view_config(name="disqus_comments",
             renderer="kotti_disqus:templates/disqus_comments.pt")
def disqus_comments_view(context, request):
    settings = get_settings_util()
    available = settings.get('kotti_disqus-disqus_available_types', [])
    available += get_settings()['kotti_disqus.extra_types'].split()

    resolver = DottedNameResolver(None)
    types = tuple(resolver.resolve(typ) for typ in available)

    if not isinstance(context, types):
        raise PredicateMismatch()

    api = template_api(context, request)
    disqus_url = ''
    disqus_shortname = settings['kotti_disqus-disqus_shortname']

    base_url = settings['kotti_disqus-disqus_base_url'].strip('/')

    if base_url:
        disqus_url = base_url + api.url(context)[len(request.application_url):]
    else:
        disqus_url = api.url(context)

    return {
        'disqus_shortname': disqus_shortname,
        'disqus_url': disqus_url,
    }


def includeme(config):
    assign_slot('disqus_comments', 'belowcontent')
