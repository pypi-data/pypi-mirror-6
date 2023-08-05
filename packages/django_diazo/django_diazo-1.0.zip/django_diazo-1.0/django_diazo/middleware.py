import os
from lxml import etree
from logging import getLogger
from diazo.wsgi import DiazoMiddleware
from diazo.utils import quote_param
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django_diazo.utils import get_active_theme
from repoze.xmliter.serializer import XMLSerializer

from django_diazo.settings import DOCTYPE


class DjangoDiazoMiddleware(object):
    """
    Django middleware wrapper for Diazo in Django.
    """
    def __init__(self):
        self.app = None
        self.theme_id = None
        self.diazo = None
        self.transform = None
        self.params = {}

    def themes_enabled(self, request):
        """
        Check if themes are enabled for the current session/request.
        """
        if settings.DEBUG and request.GET.get('theme') == 'none':
            return False
        if 'sessionid' not in request.COOKIES:
            return True
        session = SessionStore(session_key=request.COOKIES['sessionid'])
        return session.get('django_diazo_theme_enabled', True)

    def process_response(self, request, response):
        if self.themes_enabled(request):
            theme = get_active_theme(request)
            if theme:
                rules_file = os.path.join(theme.theme_path(), 'rules.xml')
                if theme.id != self.theme_id or not os.path.exists(rules_file) or theme.debug:
                    if not theme.builtin:
                        if theme.rules:
                            fp = open(rules_file, 'w')
                            try:
                                fp.write(theme.rules.serialize())
                            finally:
                                fp.close()

                    self.theme_id = theme.id

                    self.diazo = DiazoMiddleware(
                        app=self.app,
                        global_conf=None,
                        rules=rules_file,
                        prefix=theme.theme_url(),
                        doctype=DOCTYPE,
                    )
                    compiled_theme = self.diazo.compile_theme()
                    self.transform = etree.XSLT(compiled_theme, access_control=self.diazo.access_control)
                    self.params = {}
                    for key, value in self.diazo.environ_param_map.items():
                        if key in request.environ:
                            if value in self.diazo.unquoted_params:
                                self.params[value] = request.environ[key]
                            else:
                                self.params[value] = quote_param(request.environ[key])

                try:
                    content = etree.fromstring(response.content, etree.HTMLParser())
                    result = self.transform(content, **self.params)
                    response.content = XMLSerializer(result, doctype=DOCTYPE).serialize()
                except Exception, e:
                    getLogger('django_diazo').error(e)
        return response
