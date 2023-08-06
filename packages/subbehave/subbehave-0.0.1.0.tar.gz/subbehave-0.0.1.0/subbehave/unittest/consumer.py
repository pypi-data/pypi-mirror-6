from unittest.runner import TextTestRunner

from .result import PyunitResult

class PyunitConsumer(TextTestRunner):
    resultclass = PyunitResult
