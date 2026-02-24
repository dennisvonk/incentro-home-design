import os

from PIL import Image

from src.llm_client import LlmClient
from src.config import Configuration


class ImageProcessor:


    def __init__(self, config: Configuration, llm_client: LlmClient):
        self.llm_client = llm_client
        self.config = config


    def insert_asset_into_room(self, furniture_file_name: str, room_file_name: str, asset_dimensions: str) -> Image:
        room_img_path = self.config.get_room_image_path(room_file_name)
        print(f"Room image path: {room_img_path}")
        furniture_img_path = self.config.get_asset_image_path(furniture_file_name)
        print(f"Furniture image path: {furniture_img_path}")

        if not os.path.exists(room_img_path):
            raise FileNotFoundError(f"Room image not found: {room_img_path}")
        if not os.path.exists(furniture_img_path):
            raise FileNotFoundError(f"Furniture image not found: {furniture_img_path}")

        room_image = Image.open(room_img_path)

        # step 1: determine dimensions in room
        room_dimensions = self.llm_client.get_asset_dimensions(room_image)

        # step 2: get the location and orientation of the asset
        asset_location_orientation = self.llm_client.get_asset_location_orientation(room_image)

        # step 3: remove furniture from room
        room_without_asset = self.llm_client.remove_asset_from_image(room_image)

        # step 4: combine new furniture piece with room where old furniture piece is remove into one image
        resulting_image = self.llm_client.combine_images(room_without_asset, furniture_img_path, room_dimensions, asset_dimensions, asset_location_orientation)

        return resulting_image

