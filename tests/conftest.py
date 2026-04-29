import sys
from unittest.mock import MagicMock

sys.modules.setdefault("langchain_ollama", MagicMock())
