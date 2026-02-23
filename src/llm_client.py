import google.genai as genai
from google.genai import types
# from google.genai.errors import ServerError

from PIL import Image
from google.api_core import exceptions

from src.config import Configuration
from src.exceptions import LlmUnavailableError


class LlmClient:
    def __init__(self, config: Configuration):
        self.config = config
        self.client = genai.Client(api_key=self.config.llm_api_key)


    def cleanup_images(self, room: Image) -> Image:
        """Sends the room image to the LLM to remove the existing furniture."""
        prompt = """
        Remove the sofa from the image. Create a clean, sharp, highres image with soft ambient lighting without changing the original image too much.
        """

        print(f"Cleanup the image with prompt:\n{prompt}")

        response = self.client.models.generate_content(
            model=self.config.llm_model_name_image_processing,
            contents=[prompt, room],
            config=types.GenerateContentConfig(
                system_instruction="you are an expert in image composition, creating clean, sharp, highres image with soft ambient lighting without changing the original image too much",
                candidate_count=1,
                temperature=0
            )
        )

        if response.parts is not None:
            print("Removed sofa from the image!")
            return response.parts[0].as_image()

        raise RuntimeError("image cleanup failed")


    def combine_images(self, original_room_image: Image, room_image_with_missing_asset: Image, asset_image: Image, room_dimensions: str, asset_dimensions: str) -> Image:
        """
        Sends the room and furniture images to the LLM to combine them.
        """

        prompt = f"""
        The goal is to replace the original sofa in image 1 with the new sofa of image 3.
        
        Step 1: Determine where the sofa is situated in the room.
            For this step you use image 1 and use this image ONLY to determine where the original sofa is placed
            Remember where to place the new sofa based on the location of the current location in the room.
        
        Step 2: These are the dimensions of various assets in the living room in image 1: 
            {room_dimensions}
            DON'T use image 1 for anything else.
        
        Step 3: Place the new sofa
            Create a new image based on image 2 and 3.
            Image 3 is the new sofa that needs to be merged with image 2 on the correct place as determined in step 1. Make it look like the sofa was always there.
            This sofa image must remain EXACTLY THE SAME, you are only allowed to scale it appropriately. 
            Use the previously mentioned room dimensions and these dimensions of the sofa to scale correctly in the resulting image:
            {asset_dimensions} 
            Image 2 is used as a base to place the new sofa. Use this as the exact background environment for the image merge. 

        Step 4: Add realistic shadows underneath the new sofa and highlights on the sofa are consistent with the sunlight in the scene. 
        """
        # add a try - raise 503 unavailable error if the LLM call fails, so we can retry in the image processor
        try:
            response = self.client.models.generate_content(
                model=self.config.llm_model_name_image_processing,
                contents=[prompt, original_room_image, room_image_with_missing_asset, asset_image],
                config=types.GenerateContentConfig(
                    system_instruction="je bent een expert in image composition",
                    candidate_count=1,
                    temperature=0
                    # response_mime_type="image/png"
                )
            )
        # except ServerError as e:
        #     raise LlmUnavailableError from e
        except exceptions.GoogleAPICallError as e:
            raise LlmUnavailableError("LLM API call failed")

        print("Afbeelding succesvol gegenereerd!")
        return response.parts[0].as_image()


    def get_asset_dimensions(self, room_image) -> str:
        prompt = """
        Estimate the size of ALL the assets you see in the image.
        Most important size is the area that each asset takes up so this can be used in a later request to LLM to replace an asset in the image.
        reply depth, width and height in cms and area in cm2 and use this format:
        
        [asset-name-1]: area=[area], depth=[depth], width=[width], height=[height]
        [asset-name-2]: area=[area], depth=[depth], width=[width], height=[height]
        ...
        
        don't use any leading sentence, just deliver the dimensions in the format described.
        """

        response = self.client.models.generate_content(
            model=self.config.llm_model_name_dimensions,
            contents=[prompt, room_image],
            # config=types.GenerateContentConfig(
            #     system_instruction="you are an expert in image recognition and you are the best in estimating the size of assets in a picture based on your experience",
            # )
        )

        dimensions = ""
        for part in response.parts:
            if part.text is not None:
                dimensions = dimensions + part.text

        return dimensions
