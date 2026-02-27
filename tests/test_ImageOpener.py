import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock

from PIL import Image

from src.ImageOpener import ImageOpener


class TestImageOpener(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory and mock configuration for tests."""
        self.test_dir = tempfile.mkdtemp()

        # Create a dummy image file
        self.image_path = os.path.join(self.test_dir, "test_image.png")
        self.image = Image.new('RGB', (100, 100), color='red')
        self.image.save(self.image_path)

        # Create a non-image file
        self.non_image_path = os.path.join(self.test_dir, "not_an_image.txt")
        with open(self.non_image_path, "w") as f:
            f.write("this is not an image")

        # Create a subdirectory for directory tests
        self.sub_dir = os.path.join(self.test_dir, "sub")
        os.makedirs(self.sub_dir)
        self.image_in_subdir_path = os.path.join(self.sub_dir, "image_in_dir.png")
        self.image.save(self.image_in_subdir_path)

        # Create an empty directory
        self.empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(self.empty_dir)

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def test_open_image_with_file_path(self):
        """Test opening a valid image from a direct file path."""
        opened_image = ImageOpener.open_image(self.image_path)
        self.assertIsInstance(opened_image, Image.Image)
        self.assertEqual(opened_image.size, (100, 100))

    def test_open_image_with_directory_path(self):
        """Test opening an image from a directory path."""
        opened_image = ImageOpener.open_image(self.sub_dir)
        self.assertIsInstance(opened_image, Image.Image)
        self.assertEqual(opened_image.size, (100, 100))

    def test_open_image_with_non_existent_path(self):
        """Test opening a non-existent file path raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            ImageOpener.open_image("non_existent_file.png")

    def test_open_image_with_empty_directory(self):
        """Test opening an empty directory raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            ImageOpener.open_image(self.empty_dir)

    def test_open_image_with_non_image_file(self):
        """Test opening a non-image file raises ValueError."""
        with self.assertRaises(ValueError):
            ImageOpener.open_image(self.non_image_path)


if __name__ == '__main__':
    unittest.main()

