# -*- coding: utf-8 -*-

from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import dictrepr
from pyramid import security


_ = lambda x: x

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
            ('View function name', '.'.join((event['view'].__module__, event['view'].__name__))),
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
        context = getattr(self.request, 'context')
        userids = {
            'Unauthenticated': security.unauthenticated_userid(request),
            'Authenticated': security.authenticated_userid(request),
        }
        principals = security.effective_principals(request)

        #view_required_permission = ''
        #security.principals_allowed_by_permission(context, permission)

        vars.update({
            'userids': userids.items(),
            'principals': principals,
            'context_acl': context.__acl__,
            'views': self.views,
        })

        return self.render(
            'pyramid_debugtoolbar_security:templates/security_vars.dbtmako',
            vars,
            request=self.request)
