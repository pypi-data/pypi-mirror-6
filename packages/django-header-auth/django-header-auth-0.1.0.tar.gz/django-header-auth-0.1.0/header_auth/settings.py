from django.conf import settings


"""
The dict containing the header/token pairs to check.
"""
HEADER_AUTH = getattr(settings, 'HEADER_AUTH', {})
