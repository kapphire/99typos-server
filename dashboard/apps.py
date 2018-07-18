from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        import dashboard.signals  # noqa
