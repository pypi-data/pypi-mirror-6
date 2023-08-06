__version__ = "0.3.2"

try:
    from django.db.models import BinaryField  # noqa
except ImportError:
    from .models import BinaryField  # noqa
