"""
taipan
"""
__version__ = "0.0.1"
__description__ = "General purpose toolkit for Python"
__author__ = "Karol Kuczmarski"
__license__ = "Simplified BSD"


# Generic object manipulation

__missing = object()


def cast(type_, obj, default=__missing):
    try:
        return type_(obj)
    except TypeError:
        if default is __missing:
            raise
        return default
