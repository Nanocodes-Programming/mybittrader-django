from django.apps import AppConfig


class UserCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_core'
    
    def ready(self):
        import user_core.signals
