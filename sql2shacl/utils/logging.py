"""
Copyright 2024 Lukas Kubelka and Xuemin Duan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import logging
from logging.config import dictConfig


def setup_logging(log_level=logging.INFO, log_file=None):
    handlers = {}

    if not log_file:
        handlers["console"] = {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        }

    if log_file:
        handlers["file"] = {
            "level": log_level,
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": log_file,
            "mode": "a",
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": handlers,
        "root": {"level": log_level, "handlers": list(handlers.keys())},
        "loggers": {
            "mypackage": {
                "level": log_level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            }
        },
    }

    dictConfig(logging_config)
