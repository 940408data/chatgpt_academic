import logging

from rich.logging import RichHandler
from rich.traceback import install
import traceback
install(show_locals=True)
from rich.console import Console
console = Console()


logging.basicConfig(
    level="NOTSET", 
    format="%(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S.%f", 
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger('demo')