#!/usr/bin/env python
import logging
import os
import sys
import yaml
from dateutil.tz import tzlocal, tzutc

from logging import config
from grafanasync.formatters import JsonFormatter,LogfmtFormatter

# Supported Timezones for time format (in ISO 8601)
LogTimezones = {
    'LOCAL': tzlocal(),
    'UTC': tzutc()
}

# Get configuration
level = os.getenv("LOG_LEVEL", logging.INFO)
fmt = os.getenv("LOG_FORMAT", 'JSON')
tz = os.getenv("LOG_TZ", 'LOCAL')
log_conf_file = os.getenv("LOG_CONFIG","")
log_tz = LogTimezones[tz.upper()] if LogTimezones.get(tz.upper()) else LogTimezones['LOCAL']

# Supported Log Formatters
LogFormatters = {
    'JSON': (JsonFormatter('%(levelname)s %(message)s',
                           rename_fields={"message": "msg", "levelname": "level"})),
    'LOGFMT': (LogfmtFormatter(keys=["time", "level", "msg"],
                               mapping={"time": "asctime", "level": "levelname", "msg": "message"}))
}

logLevel = level.upper() if isinstance(level, str) else level
log_fmt = LogFormatters[fmt.upper()] if LogFormatters.get(fmt.upper()) else LogFormatters['JSON']

default_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": logLevel,
        "handlers": [
            "console"
        ]
    },
    "handlers": {
        "console": {
        "class": "logging.StreamHandler",
        "level": logLevel,
        "formatter": fmt.upper()
        }
    },
    "formatters": {
        "JSON": {
            "()": "grafanasync.formatters.JsonFormatter",
            "format": "%(levelname)s %(message)s",
            "rename_fields": {
                "message": "msg",
                "levelname": "level"
            }
        },
        "LOGFMT": {
            "()": "grafanasync.formatters.LogfmtFormatter",
            "keys": [
                "time",
                "level",
                "msg"
            ],
            "mapping": {
                "time": "asctime",
                "level": "levelname",
                "msg": "message"
            }
        }
    }
}

def get_log_config():
    if log_conf_file != "" :
        try:
            with open(log_conf_file, 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)
            return config
        except FileNotFoundError:
            msg = "Config file: "+ log_conf_file + " Not Found"
            print(msg)
            sys.exit(1)
        except yaml.YAMLError as e:
            print("Error loading yaml file:")
            print(e)
            sys.exit(2)
    else:
        return default_log_config    

# Initialize/configure root logger
log_config = get_log_config()    
config.dictConfig(log_config)

def get_logger():
    return logging.getLogger('grafana-k8s-sidecar')