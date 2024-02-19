from django.apps import AppConfig


class PersonasConfig(AppConfig):
    name = 'personas'


class MutualConfig(AppConfig):
    name = 'mutual'
    
    def ready(self):
        import mutual.signals 
