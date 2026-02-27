import os

from PIL import Image, UnidentifiedImageError

from src.config import Configuration


class ImageOpener:
    @staticmethod
    def open_image(path):
        """
        Find a file in [path] and if this file is an image, return this as a PIL.Image. Otherwise raise an exception.
        If [path] is a directory, it will try to open the first file found in that directory.

        Args:
            path (str): a path to an image file or a directory containing one.

        Returns:
            Image: when a file is found, return this as a PIL Image.

        Raises:
            FileNotFoundError: If the path does not exist, or if it's an empty directory.
            ValueError: If the file is not a valid or supported image format.
        """
        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            if not files:
                raise FileNotFoundError(f"No files found in directory: {path}")
            path = os.path.join(path, files[0])

        if not os.path.isfile(path):
            raise FileNotFoundError(f"No file found at path: {path}")
        try:
            image = Image.open(path)
            return image
        except UnidentifiedImageError:
            raise ValueError(f"The file at {path} is not a valid image.")
