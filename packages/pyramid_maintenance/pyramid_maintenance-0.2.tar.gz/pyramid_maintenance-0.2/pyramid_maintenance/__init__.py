from pyramid.interfaces import IRootFactory
from pyramid.response import Response
from pyramid.renderers import render

import re


def tween_maintenance(handler, registry):
    """
        Tween maintenance

        To enable it, please add in your .ini file:
        pyramid.tweens = pyramid_maintenance.tween_maintenance

        # List of permissions (separeted by comma, space, carriage return and/or new line).
        # The pyramid app isn't in maintenance mode for people who have one of these permissions.
        pyramid_maintenance.permissions = permission1, permission2
        # Relative path from defined template location directories.
        pyramid_maintenance.template = template.mako
        
    """
    permissions = filter(bool, map(str.strip, re.split(',|\t|\s', registry.settings['pyramid_maintenance.permissions'])))
    template = registry.settings['pyramid_maintenance.template']

    def doer(request):
        rootfactory = request.registry.queryUtility(IRootFactory)

        for permission in permissions:
            if request.has_permission(permission, rootfactory):
                return handler(request)

        return Response(render(template, {'title':''}, request))


    return doer
