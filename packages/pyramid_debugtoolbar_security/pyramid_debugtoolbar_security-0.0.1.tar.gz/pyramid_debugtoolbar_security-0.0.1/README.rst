=============================
pyramid_debugtoolbar_security
=============================

pyramid_debugtoolbar_security is a security panel for pyramid_debugtoolbar
(principals, context acl, view information except view's permission).


Usage
=====

Put panel definition on your ini file::

   debugtoolbar.panels =
       pyramid_debugtoolbar_security.SecurityVarsDebugPanel

If you need other panels too::

   debugtoolbar.panels =
       pyramid_debugtoolbar.panels.versions.VersionDebugPanel
       pyramid_debugtoolbar.panels.settings.SettingsDebugPanel
       pyramid_debugtoolbar.panels.headers.HeaderDebugPanel
       pyramid_debugtoolbar.panels.request_vars.RequestVarsDebugPanel
       pyramid_debugtoolbar.panels.renderings.RenderingsDebugPanel
       pyramid_debugtoolbar.panels.logger.LoggingPanel
       pyramid_debugtoolbar.panels.performance.PerformanceDebugPanel
       pyramid_debugtoolbar.panels.routes.RoutesDebugPanel
       pyramid_debugtoolbar.panels.sqla.SQLADebugPanel
       pyramid_debugtoolbar.panels.tweens.TweensDebugPanel
       pyramid_debugtoolbar.panels.introspection.IntrospectionDebugPanel
       pyramid_debugtoolbar_security.SecurityVarsDebugPanel

License
=======

Apache Software License 2.0


History
=======

0.0.1 (2014/2/6)
------------------

* panel provids: user ids, principals, context acl, view name, view function, renderer and route information.

