import logging
import sys

import structlog


def configure_logging() -> None:
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.EventRenamer("message"),
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(processors=processors)

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
