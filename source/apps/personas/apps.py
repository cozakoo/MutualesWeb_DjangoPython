from django.apps import AppConfig


class PersonasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    name = 'apps.personas'


# class MutualConfig(AppConfig):
#     name = 'mutual'
    
#     def ready(self):
#         import mutual.signals 
