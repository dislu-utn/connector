from typing import Literal
import unittest
from src.connector import Connector

class BaseTest(unittest.TestCase):

    def initialize(self, origin: Literal["dislu", "adaptaria"]):
        self.connector = Connector(origin)

