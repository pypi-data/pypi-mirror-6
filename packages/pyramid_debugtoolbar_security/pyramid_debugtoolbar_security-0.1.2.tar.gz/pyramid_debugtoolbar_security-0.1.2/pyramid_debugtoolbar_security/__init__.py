# -*- coding: utf-8 -*-

from zope.interface import providedBy
from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import dictrepr
from pyramid import security
from pyramid.interfaces import IView, IViewClassifier


_ = lambda x: x


def get_view(request, context):
    provides = [IViewClassifier, request.request_iface, providedBy(context)]
    view = request.registry.adapters.lookup(
        provides, IView, name='', default=None)
    return view


def format_view_name(view):
    try:
        return '.'.join((view.__module__, view.__name__))
    except:
        return str(view)


def get_view_permission(request, view):
    categorized = dict(request.registry.introspector.categorized())
    for entry in categorized.get('views', []):
        intro = entry['introspectable']
        if intro.get('derived_callable') is view:
            for ref in entry['related']:
                if ref.type_name == 'permission':
                    return ref.title


class SecurityVarsDebugPanel(DebugPanel):
    """
    A panel to display security related variables (principals, acls,
    permissions).
    """
    name = 'SecurityVars'
    has_content = True
    views = ()

    def process_beforerender(self, event):
        if not self.views:
            self.views = []
        name = event['renderer_info'].name
        if name and name.startswith(('pyramid_debugtoolbar', 'pyramid_debugtoolbar_security')):
            return
        request = event.get('request')
        info = (
            ('Renderer name', name),
            ('Route', 'name={0.name!r}, path={0.path!r}'.format(request.matched_route)),
            ('View name', request.view_name),
            ('View function name', format_view_name(event.get('view'))),
        )

        self.views.append(dict(info=info, system=dictrepr(event)))

    def nav_title(self):
        return _('Security Vars')

    def title(self):
        return _('Security Vars')

    def url(self):
        return ''

    def content(self):
        vars = {}
        request = self.request
        context = getattr(self.request, 'context', None)
        context_acl = getattr(context, '__acl__', [])
        userids = {
            'Unauthenticated': security.unauthenticated_userid(request),
            'Authenticated': security.authenticated_userid(request),
        }
        principals = security.effective_principals(request)

        pinfo = []
        view = get_view(request, context)
        if view:
            pinfo.append(('view', view))
            pinfo.append(('view name', format_view_name(view)))
            p = get_view_permission(request, view)
            pinfo.append(('permission', p))
            pinfo.append(('allowed principals',
                sorted(security.principals_allowed_by_permission(context, p))
            ))

        vars.update({
            'userids': userids.items(),
            'principals': principals,
            'context_acl': context_acl,
            'permission_info': pinfo,
            'views': self.views,
        })

        return self.render(
            'pyramid_debugtoolbar_security:templates/security_vars.dbtmako',
            vars,
            request=self.request)
