from datetime import datetime

from django.utils import timezone


def local_datetime(year, month, day):
    """
    Returns a timezone aware version of a date, using the current timezone.
    """

    date = datetime(year, month, day)
    return timezone.make_aware(date, timezone.get_current_timezone())


def local_datetime_today():
    """
    Returns today at midnight as a timezone aware datetime object, using the
    current timezone.
    """

    today = timezone.now()
    return local_datetime(today.year, today.month, today.day)
