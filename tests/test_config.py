import unittest
from operator import contains

from src.config import Configuration


class MyTestCase(unittest.TestCase):
    def test_get_room_image_path(self):
        config = Configuration("test-1")
        self.assertTrue(contains(config.get_room_image_path("kamer.jpg"), "tests\\resources\\test-1\\input\\room\\kamer.jpg"))

    def test_get_furniture_image_path(self):
        config = Configuration("test-1")
        self.assertTrue(contains(config.get_furniture_image_path("meubel.jpg"), "tests\\resources\\test-1\\input\\furniture\\meubel.jpg"))

if __name__ == '__main__':
    unittest.main()
