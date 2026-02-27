import os
import unittest
from operator import contains

from PIL import Image

# Load environment variables from gemini.env
# IMPORTANT: make sure this is done before importing any module that relies on these environment variables (like Configuration or LlmClient)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('gemini.env'))
############

from src.ImageOpener import ImageOpener
from src.config import Configuration
from src.llm_client import LlmClient
from src.exceptions import LlmUnavailableError

CONFIGS = [("test-sofa",
                {"dimension_items": {"sofa", "rug", "plant"},
                "room_dimensions": """
                    Dimensions: 
                    sectional sofa: area=62000 cm2, depth=100 cm, width=620 cm, height=75 cm
                    coffee table: area=4800 cm2, depth=60 cm, width=80 cm, height=35 cm
                    rug: area=60000 cm2, depth=200 cm, width=300 cm, height=1 cm
                    plant: area=2500 cm2, depth=50 cm, width=50 cm, height=180 cm
                    fireplace: area=4000 cm2, depth=30 cm, width=120 cm, height=150 cm
                    wall art (large vertical): area=3000 cm2, depth=3 cm, width=50 cm, height=60 cm
                    wall art (small vertical): area=1800 cm2, depth=3 cm, width=30 cm, height=60 cm
                    wall art (small horizontal): area=1500 cm2, depth=3 cm, width=50 cm, height=30 cm
                    wall art (square): area=2500 cm2, depth=3 cm, width=50 cm, height=50 cm
                    pendant light: area=500 cm2, depth=10 cm, width=100 cm, height=50 cm (fixture only, not including cable length)""",
                "asset_dimensions": """
                    Hoogte=80 cm
                    Poot hoogte=2 cm
                    Minimale zitdiepte=60 cm
                    Maximale zitdiepte=90 cm
                    Zithoogte=42 cm
                    Rughoogte=40 cm
                    Breedte armleuning=30 cm
                    Hoogte arm=50 cm""",
                "asset_location_orientation": """
                    location: The sofa is in the center of the room, in front of the wall with pictures and to the left of the fireplace.
                    orientation: The sofa is facing towards the viewer."""}
            ),
           ("test-bed",
            {
                "dimension_items": {"width", "depth", "height"},
                "room_dimensions": """
                    Dimensions:
                    wardrobe: area=76500cm2, depth=60cm, width=450cm, height=255cm
                    bed: area=44000cm2, depth=220cm, width=200cm, height=120cm
                    nightstand_left: area=3000cm2, depth=40cm, width=75cm, height=60cm
                    nightstand_right: area=3000cm2, depth=40cm, width=75cm, height=60cm
                    rug: area=49087cm2, depth=250cm, width=250cm, height=1cm
                    ottoman: area=4000cm2, depth=80cm, width=50cm, height=40cm
                    plant: area=4000cm2, depth=50cm, width=50cm, height=160cm""",
                "asset_dimensions": """
                    width: 181.6 cm
                    depth: 208.7 cm
                    height bed: 45.2 cm
                    height backboard: 107.8 cm """,
                "asset_location_orientation": """
                    location: The bed is located in the center-right of the room, positioned between a large wooden wardrobe on the left and a window on the right.
                    orientation: The head of the bed is oriented towards the back wall, with the foot of the bed facing towards the viewer."""}
            )]

class MyTestCase(unittest.TestCase):


    def test_determine_dimensions(self):
        for config_props in CONFIGS:
            with self.subTest(config=config_props):
                # unpack tuple (name, prop_set)
                config_name, prop_set = config_props

                # init
                config = Configuration(config_name)

                # create input image object
                room_image_path = config.get_room_image_path("room.jpg")
                room_img = Image.open(room_image_path)

                # call llm client to get the asset dimensions from the image
                client = LlmClient(config)
                dimensions = client.get_asset_dimensions(room_img)
                self.assertIsNotNone(dimensions)

                # print results for manual inspection
                print(f"Dimensions:\n{dimensions}")

                print(f"Expected dimensions:\n{prop_set[0]['dimension_items']}")
                for check_dimension in prop_set[0]["dimension_items"]:
                    self.assertTrue(contains(dimensions.casefold(), check_dimension))

    def test_determine_asset_location_orientation (self):
        for config_props in CONFIGS:
            with self.subTest(config=config_props):
                # unpack tuple (name, prop_set)
                config_name, _ = config_props
                # init
                config = Configuration(config_name)

                # create input image object
                room_image_path = config.get_room_image_path("room.jpg")
                room_img = Image.open(room_image_path)

                # call llm client to get the asset dimensions from the image
                client = LlmClient(config)
                description = client.get_asset_location_orientation(room_img, config_name.split('-')[1])
                self.assertIsNotNone(description)

                # print results for manual inspection
                print(f"Description location & orientation:\n{description}")

                self.assertTrue(contains(description.casefold(), "location:"))
                self.assertTrue(contains(description.casefold(), "orientation:"))

    def test_remove_asset_from_image(self):
        for config_props in CONFIGS:
            with self.subTest(config=config_props):
                # unpack tuple (name, prop_set)
                config_name, _ = config_props

                # init
                config = Configuration(config_name)
                client = LlmClient(config)

                # cleanup old image
                if os.path.exists(f'{config.output_path}\\room-without-asset.png'):
                    os.remove(f'{config.output_path}\\room-without-asset.png')

                # create input image object
                room_image_path = config.get_room_image_path("room.jpg")
                room_img = Image.open(room_image_path)

                # call llm client to remove the sofa from the image
                image_without_asset = client.remove_asset_from_image(room_img, config_name.split('-')[1])
                self.assertIsNotNone(image_without_asset)

                # save image for manual inspection
                image_without_asset.save(f'{config.output_path}\\room-without-asset.png')
                self.assertTrue(os.path.exists(f'{config.output_path}\\room-without-asset.png'))


    def test_place_new_asset_in_empty_room(self):
        for config_props in CONFIGS:
            with self.subTest(config=config_props):
                # unpack tuple (name, prop_set)
                config_name, prop_set = config_props

                # init
                config = Configuration(config_name)
                client = LlmClient(config)

                # load images
                room_image_with_missing_asset = Image.open(f'{config.output_path}\\room-without-asset.png')
                asset_image = ImageOpener.open_image(config.get_asset_image_path(''))

                # define prompts
                print(f"Using room dimensions:\n{prop_set['room_dimensions']}")
                room_dimensions = prop_set['room_dimensions']

                print(f"Using asset dimensions:\n{prop_set['asset_dimensions']}")
                asset_dimensions = prop_set['asset_dimensions']

                print(f"Using asset location_orientation:\n{prop_set['asset_location_orientation']}")
                asset_location_orientation = prop_set['asset_location_orientation']

                try:
                    # call llm client to combine the images
                    room_with_new_asset = client.combine_images(room_image_with_missing_asset, asset_image, room_dimensions, asset_dimensions, asset_location_orientation)
                    room_with_new_asset.save(f'{config.output_path}\\room_with_new_asset.png')
                    self.assertTrue(os.path.exists(f'{config.output_path}\\room_with_new_asset.png'))

                except LlmUnavailableError as e:
                    self.fail(f"LLM failed to combine images: {e}")

    def test_10x_place_new_asset_in_empty_room(self):
        for config_props in CONFIGS:
            with self.subTest(config=config_props):
                # init
                config = Configuration(config_props)
                client = LlmClient(config)

                # load images
                room_image_with_missing_asset = Image.open(f'{config.output_path}\\room-without-asset.png')
                asset_image = Image.open(config.get_asset_image_path('asset.png'))

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