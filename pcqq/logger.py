import sys
import logging


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    datefmt="%Y/%m/%d-%H:%M:%S",
    format='[%(name)s %(asctime)s] %(levelname)s: %(message)s'
)

logger = logging.getLogger('PCQQ')
logger.fatal = sys.exit
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

sys.modules[__name__] = logger
