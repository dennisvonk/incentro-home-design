import unittest
from operator import contains

from src.config import Configuration


class MyTestCase(unittest.TestCase):
    def test_get_room_image_path(self):
        config = Configuration("test-1")
        self.assertTrue(contains(config.get_room_image_path("room.jpg"), "tests\\resources\\test-1\\input\\room\\room.jpg"))

    def test_get_asset_image_path(self):
        config = Configuration("test-1")
        self.assertTrue(contains(config.get_asset_image_path("asset.png"), "tests\\resources\\test-1\\input\\asset\\asset.png"))

if __name__ == '__main__':
    unittest.main()
