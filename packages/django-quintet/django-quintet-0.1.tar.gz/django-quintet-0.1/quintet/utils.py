# -*- coding: utf-8 -*-
from django.forms.util import to_current_timezone

def tz_strftime(datetime, format):
    """Format a datetime in the current timezone."""
    corrected = to_current_timezone(datetime)
    return corrected.strftime(format)

def tz_localize(datetime):
    """Localize a datetime in the current timezone."""
    from django.utils.formats import localize
    corrected = to_current_timezone(datetime)
    return localize(corrected)
