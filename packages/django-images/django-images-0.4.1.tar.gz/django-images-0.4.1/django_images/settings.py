from django.conf import settings

IMAGE_PATH = getattr(settings, 'IMAGE_PATH', None)
IMAGE_SIZES = getattr(settings, 'IMAGE_SIZES', {})
