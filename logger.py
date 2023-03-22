import logging

__all__ = ['logger']

logger = logging.getLogger("PY-PCQQ")
logger.setLevel(logging.INFO)

steram_handler = logging.StreamHandler()
steram_formatter = logging.Formatter("[%(name)s] %(message)s")
steram_handler.setFormatter(steram_formatter)
logger.addHandler(steram_handler)