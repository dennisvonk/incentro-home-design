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


    def test_remove_from_image(self):
        # init
        config = Configuration("test-1")
        client = LlmClient(config)

        # cleanup old image
        if os.path.exists(f'{config.output_path}\\room-without-sofa.png'):
            os.remove(f'{config.output_path}\\room-without-sofa.png')

        # create input image object
        room_image_path = config.get_room_image_path("kamer.jpg")
        room_img = Image.open(room_image_path)

        # call llm client to remove the sofa from the image
        image_without_sofa = client.cleanup_images(room_img)
        self.assertIsNotNone(image_without_sofa)

        # save image for manual inspection
        image_without_sofa.save(f'{config.output_path}\\room-without-sofa.png')


    def test_place_new_sofa_in_empty_room(self):
        # init
        config = Configuration("test-1")
        client = LlmClient(config)

        # load images
        original_room_image = Image.open(config.get_room_image_path("kamer.jpg"))
        room_image_with_missing_asset = Image.open(f'{config.output_path}\\room-without-sofa.png')
        sofa_image = Image.open(config.get_furniture_image_path('meubel.png'))

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
        sofa_dimensions = """
        Hoogte=80 cm
        Poot hoogte=2 cm
        Minimale zitdiepte=60 cm
        Maximale zitdiepte=90 cm
        Zithoogte=42 cm
        Rughoogte=40 cm
        Breedte armleuning=30 cm
        Hoogte arm=50 cm
        """

        try:
            # call llm client to combine the images
            room_with_new_sofa = client.combine_images(original_room_image, room_image_with_missing_asset, sofa_image, room_dimensions, sofa_dimensions)
            room_with_new_sofa.save(f'{config.output_path}\\room_with_new_sofa.png')
        except LlmUnavailableError as e:
            self.fail(f"LLM failed to combine images: {e}")

# Hele slechte ontwikkeling:
# google.genai.errors.ServerError: 503 UNAVAILABLE.
# {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

if __name__ == '__main__':
    unittest.main()