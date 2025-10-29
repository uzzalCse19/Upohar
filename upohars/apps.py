from django.apps import AppConfig

class UpoharsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'upohars'

    def ready(self):
        import upohars.signals
