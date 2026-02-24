import os
import unittest
from operator import contains

from PIL import Image

from src.config import Configuration
from src.llm_client import LlmClient
from src.exceptions import LlmUnavailableError

class MyTestCase(unittest.TestCase):
    def test_determine_dimensions(self):
        # init
        config = Configuration("test-1")

        # create input image object
        room_image_path = config.get_room_image_path("kamer.jpg")
        room_img = Image.open(room_image_path)

        # call llm client to get the asset dimensions from the image
        client = LlmClient(config)
        dimensions = client.get_asset_dimensions(room_img)
        self.assertIsNotNone(dimensions)
        self.assertTrue(contains(dimensions.casefold(), "sofa:"))
        self.assertTrue(contains(dimensions.casefold(), "rug:"))
        self.assertTrue(contains(dimensions.casefold(), "plant:"))

        # print results for manual inspection
        print(f"Dimensions:\n{dimensions}")

    def test_determine_asset_location_orientation (self):
        # init
        config = Configuration("test-1")

        # create input image object
        room_image_path = config.get_room_image_path("kamer.jpg")
        room_img = Image.open(room_image_path)

        # call llm client to get the asset dimensions from the image
        client = LlmClient(config)
        description = client.get_asset_location_orientation(room_img)
        self.assertIsNotNone(description)
        self.assertTrue(contains(description.casefold(), "location:"))
        self.assertTrue(contains(description.casefold(), "orientation:"))

        # print results for manual inspection
        print(f"Description location & orientation:\n{description}")


    def test_remove_asset_from_image(self):
        # init
        config = Configuration("test-1")
        client = LlmClient(config)

        # cleanup old image
        if os.path.exists(f'{config.output_path}\\room-without-asset.png'):
            os.remove(f'{config.output_path}\\room-without-asset.png')

        # create input image object
        room_image_path = config.get_room_image_path("kamer.jpg")
        room_img = Image.open(room_image_path)

        # call llm client to remove the sofa from the image
        image_without_asset = client.remove_asset_from_image(room_img)
        self.assertIsNotNone(image_without_asset)

        # save image for manual inspection
        image_without_asset.save(f'{config.output_path}\\room-without-asset.png')
        self.assertTrue(os.path.exists(f'{config.output_path}\\room-without-asset.png'))


    def test_place_new_asset_in_empty_room(self):
        # init
        config = Configuration("test-1")
        client = LlmClient(config)

        # load images
        room_image_with_missing_asset = Image.open(f'{config.output_path}\\room-without-asset.png').getim()
        asset_image = Image.open(config.get_asset_image_path('meubel.png')).getim()

        # define prompts
        room_dimensions = """
        Dimensions: sectional sofa: area=62000 cm2, depth=100 cm, width=620 cm, height=75 cm
        coffee table: area=4800 cm2, depth=60 cm, width=80 cm, height=35 cm
        rug: area=60000 cm2, depth=200 cm, width=300 cm, height=1 cm
        plant: area=2500 cm2, depth=50 cm, width=50 cm, height=180 cm
        fireplace: area=4000 cm2, depth=30 cm, width=120 cm, height=150 cm
        wall art (large vertical): area=3000 cm2, depth=3 cm, width=50 cm, height=60 cm
        wall art (small vertical): area=1800 cm2, depth=3 cm, width=30 cm, height=60 cm
        wall art (small horizontal): area=1500 cm2, depth=3 cm, width=50 cm, height=30 cm
        wall art (square): area=2500 cm2, depth=3 cm, width=50 cm, height=50 cm
        pendant light: area=500 cm2, depth=10 cm, width=100 cm, height=50 cm (fixture only, not including cable length)
        """
        asset_dimensions = """
        Hoogte=80 cm
        Poot hoogte=2 cm
        Minimale zitdiepte=60 cm
        Maximale zitdiepte=90 cm
        Zithoogte=42 cm
        Rughoogte=40 cm
        Breedte armleuning=30 cm
        Hoogte arm=50 cm
        """
        asset_location_orientation = """
        location: The sofa is in the center of the room, in front of the wall with pictures and to the left of the fireplace.
        orientation: The sofa is facing towards the viewer.
        """

        try:
            # call llm client to combine the images
            room_with_new_asset = client.combine_images(room_image_with_missing_asset, asset_image, room_dimensions, asset_dimensions, asset_location_orientation)
            room_with_new_asset.save(f'{config.output_path}\\room_with_new_asset.png')
            self.assertTrue(os.path.exists(f'{config.output_path}\\room_with_new_asset.png'))

        except LlmUnavailableError as e:
            self.fail(f"LLM failed to combine images: {e}")

    def test_10x_place_new_asset_in_empty_room(self):
        # init
        config = Configuration("test-1")
        client = LlmClient(config)

        # load images
        room_image_with_missing_asset = Image.open(f'{config.output_path}\\room-without-asset.png')
        asset_image = Image.open(config.get_asset_image_path('meubel.png'))

        # define prompts
        room_dimensions = """
        Dimensions: sectional sofa: area=62000 cm2, depth=100 cm, width=620 cm, height=75 cm
        coffee table: area=4800 cm2, depth=60 cm, width=80 cm, height=35 cm
        rug: area=60000 cm2, depth=200 cm, width=300 cm, height=1 cm
        plant: area=2500 cm2, depth=50 cm, width=50 cm, height=180 cm
        fireplace: area=4000 cm2, depth=30 cm, width=120 cm, height=150 cm
        wall art (large vertical): area=3000 cm2, depth=3 cm, width=50 cm, height=60 cm
        wall art (small vertical): area=1800 cm2, depth=3 cm, width=30 cm, height=60 cm
        wall art (small horizontal): area=1500 cm2, depth=3 cm, width=50 cm, height=30 cm
        wall art (square): area=2500 cm2, depth=3 cm, width=50 cm, height=50 cm
        pendant light: area=500 cm2, depth=10 cm, width=100 cm, height=50 cm (fixture only, not including cable length)
        """
        asset_dimensions = """
        Hoogte=80 cm
        Poot hoogte=2 cm
        Minimale zitdiepte=60 cm
        Maximale zitdiepte=90 cm
        Zithoogte=42 cm
        Rughoogte=40 cm
        Breedte armleuning=30 cm
        Hoogte arm=50 cm
        """
        asset_location_orientation = """
        location: The sofa is in the center of the room, in front of the wall with pictures and to the left of the fireplace.
        orientation: The sofa is facing towards the viewer.
        """

        # create folder 'loop' if it doesn't exist
        if not os.path.exists(f'{config.output_path}\\loop'):
            os.makedirs(f'{config.output_path}\\loop')


        for i in range(10):
            try:
                # call llm client to combine the images
                room_with_new_asset = client.combine_images(room_image_with_missing_asset, asset_image, room_dimensions, asset_dimensions, asset_location_orientation)
                room_with_new_asset.save(f'{config.output_path}\\loop\\room_with_new_asset_{i}.png')
            except LlmUnavailableError as e:
                self.fail(f"LLM failed to combine images: {e}")


# Hele slechte ontwikkeling:
# google.genai.errors.ServerError: 503 UNAVAILABLE.
# {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

if __name__ == '__main__':
    unittest.main()