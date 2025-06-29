from .base.celery import app as celery_app

__all__ = ("celery_app",)

default_app_config = "transformer.apps.TransformerConfig"
