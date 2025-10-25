from django.apps import AppConfig


class StransportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stransport'
from django.apps import AppConfig

class StransportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stransport'

    def ready(self):
        import stransport.signals
