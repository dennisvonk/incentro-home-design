import os
import unittest

from src.config import Configuration
from src.image_processor import ImageProcessor
from src.llm_client import LlmClient


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_image_processing():
        # init
        config = Configuration("test-1")
        client = LlmClient(config)
        processor = ImageProcessor(config, client)

        # prompts
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


        # cleanup old image
        if os.path.exists(f'{config.output_path}\\room-without-sofa.png'):
            os.remove(f'{config.output_path}\\room-without-sofa.png')
        if os.path.exists(f'{config.output_path}\\room_with_new_sofa.png'):
            os.remove(f'{config.output_path}\\room_with_new_sofa.png')

        # call processor to insert the new sofa into room
        room_with_new_sofa = processor.insert_furniture_into_room("meubel.png", "kamer.jpg", sofa_dimensions)

        # do checks
        assert room_with_new_sofa is not None

        # save image for manual inspection
        room_with_new_sofa.save(f'{config.output_path}\\room_with_new_sofa.png')


if __name__ == '__main__':
    unittest.main()