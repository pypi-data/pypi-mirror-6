__version__ = "0.4.0"

try:
    from django.db.models import BinaryField  # noqa
except ImportError:
    from .models import BinaryField  # noqa
