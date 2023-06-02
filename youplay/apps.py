from django.apps import AppConfig


class YouplayConfig(AppConfig):
    name = "youplay"

    def ready(self):
        import youplay.signals


default_app_config = "youplay.apps.MyAppConfig"
