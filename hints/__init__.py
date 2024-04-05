"""Home-assistant INtent Text Spell-checker"""
from pathlib import Path

_DIR = Path(__file__).parent
_VERSION_PATH = _DIR / "VERSION"

__version__ = _VERSION_PATH.read_text(encoding="utf-8").strip()
__name__ = "hints"
__description__="Home-assistant INtent Text Spell-checker"
__author__ = "Cociweb"
__email__ = "example@example.org"
__license__="MIT"
__url__="http://github.com/cociweb/hints"
__package__ = __name__

__all__ = [__version__, __name__, __description__, __author__, __email__, __license__, __url__, __package__]
