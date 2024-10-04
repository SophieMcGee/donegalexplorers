from django.apps import AppConfig


class ExplorersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'explorers'

    def ready(self):
        import explorers.signals