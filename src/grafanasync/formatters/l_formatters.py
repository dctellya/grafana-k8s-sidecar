#!/usr/bin/env python
from typing import Optional
from logfmter import Logfmter
from pythonjsonlogger import jsonlogger
from datetime import datetime
import os
from dateutil.tz import tzlocal, tzutc
#from resources import list_resources, watch_for_changes, prepare_payload


#################################################
# Logging
#################################################

LogTimezones = {
    'LOCAL': tzlocal(),
    'UTC': tzutc()
}

# Get configuration
tz = os.getenv("LOG_TZ", 'LOCAL')
log_tz = LogTimezones[tz.upper()] if LogTimezones.get(tz.upper()) else LogTimezones['LOCAL']


class Iso8601Formatter:
    """
    A formatter mixin which always forces dates to be rendered in iso format.
    Using `datefmt` parameter of logging.Formatter is insufficient because of missing fractional seconds.
    """

    def formatTime(self, record, datefmt: Optional[str] = ...):
        """
        Meant to override logging.Formatter.formatTime
        """
        return datetime.fromtimestamp(record.created, log_tz).isoformat()


class JsonFormatter(Iso8601Formatter, jsonlogger.JsonFormatter):
    """
    A formatter combining json logs with iso dates
    """

    def add_fields(self, log_record, record, message_dict):
        log_record['time'] = self.formatTime(record)
        super(JsonFormatter, self).add_fields(log_record, record, message_dict)

class LogfmtFormatter(Iso8601Formatter, Logfmter):
    """
    A formatter combining logfmt style with iso dates
    """
    pass


#################################################
# End - Logging
#################################################