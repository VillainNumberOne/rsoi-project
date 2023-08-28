from django.apps import AppConfig
from api.kafka_receiver import start_kafka_processing


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"


    def ready(self):
        from . import views
        start_kafka_processing()