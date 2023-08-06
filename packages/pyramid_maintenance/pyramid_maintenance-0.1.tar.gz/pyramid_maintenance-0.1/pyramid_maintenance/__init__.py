from pyramid.interfaces import IRootFactory
from pyramid.response import Response
from pyramid.renderers import render


def tween_maintenance(handler, registry):
    """
        Tween maintenance

        To enable it, please add in your .ini file:
        pyramid.tweens = pyramid_maintenance.tween_maintenance

        # List of roles (separeted by commas), The pyramid app isn't
        # in maintenance mode for people who have one of these roles.
        pyramid_maintenance.roles = role1, role2
        # Relative path from defined template location directories.
        pyramid_maintenance.template = template.mako
        
    """
    roles = map(str.strip, registry.settings['pyramid_maintenance.roles'].split(','))
    template = registry.settings['pyramid_maintenance.template']

    def doer(request):
        rootfactory = request.registry.queryUtility(IRootFactory)

        for role in roles:
            if request.has_permission(role, rootfactory):
                return handler(request)

        return Response(render(template, {'title':''}, request))


    return doer
