from django.apps import AppConfig

# Описание конфигурации приложения.
class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals