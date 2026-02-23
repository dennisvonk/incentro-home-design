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


    def remove_asset_from_image(self, room: Image) -> Image:
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


    def combine_images(self, room_image_with_missing_asset: Image, asset_image: Image, room_dimensions: str, asset_dimensions: str, location_orientation_asset: str) -> Image:
        """
        Sends the room and furniture images to the LLM to combine them.
        """

        prompt = f"""
        The goal is to place a sofa (=image 2) in the living room (=image 1).
        
        Step 1: This is the information about the location and orientation of the new sofa:
            {location_orientation_asset}
            This information helps you place the sofa on the correct place in the living room.
        
        Step 2: These are the dimensions of various assets in the living room: 
            {room_dimensions}
            These dimensions help you determine the scale of the room and all other assets. 
        
        Step 3: These are the dimensions of the sofa:
            {asset_dimensions} 
            These dimensions of the sofa combined with the dimension of the assets in the living room help you determine the scale of the sofa.
             
        Step 4: Place the new sofa
            Generate an image where the sofa is placed in the living room:
            - on the location and orientation determined in step 1.
            - scaled properly using the dimensions provided in step 2 and step 3.
        
        Step 5: Verify
            Verify that the sofa in the new generated room looks exactly like the original provided sofa image.
            
        Step 6: Realism
            Add realistic shadows underneath the new sofa and highlights on the sofa are consistent with the sunlight in the scene. 
            
        Rules:
            - You are allowed to scale the sofa
            - MAKE NO OTHER CHANGES TO THE SOFA
            - Make no changes to the assets in the room
        """
        # add a try - raise 503 unavailable error if the LLM call fails, so we can retry in the image processor
        try:
            response = self.client.models.generate_content(
                model=self.config.llm_model_name_image_processing,
                contents=[prompt, room_image_with_missing_asset, asset_image],
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

    def get_asset_location_orientation(self, room_image) -> str:
        prompt = """
        Describe the location and the orientation of the sofa in the room.  
        Use this format:
            location: [location]
            orientation: [orientation]

        Rules:
            - location: Don't describe the form or design of the sofa, just the place where the main part of the sofa is located in relation to other assets. 
            - orientation: Don't describe the form or design of the sofa, just where the sofa is oriented to, in relation to the viewer.
            - don't use any leading sentence, deliver the information in the format described.
        """

        response = self.client.models.generate_content(
            model=self.config.llm_model_name_dimensions,
            contents=[prompt, room_image],
            config=types.GenerateContentConfig(
                system_instruction="je bent een expert in image recognition",
                candidate_count=1,
                temperature=0
            )
        )

        result = ""
        for part in response.parts:
            if part.text is not None:
                result = result + part.text

        return result
