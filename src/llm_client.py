import google.genai as genai
from google.genai import types

from PIL import Image
from google.api_core import exceptions

from src.config import Configuration
from src.exceptions import LlmUnavailableError


class LlmClient:
    def __init__(self, config: Configuration):
        self.config = config
        self.client = genai.Client(api_key=self.config.llm_api_key)


    def remove_asset_from_image(self, room, asset_name):
        """Removes an asset from an image using an LLM.

        This method sends an image of a room to a generative AI model
        and instructs it to remove a specific asset (e.g., a sofa).
        The goal is to obtain a clean image with the asset removed,
        maintaining the original image's characteristics as much as possible.

        Args:
            room (Image): A PIL Image object of the room.
            asset_name (str): The name of the asset to be removed from the image.

        Returns:
            Image: A PIL Image object with the specified asset removed.

        Raises:
            RuntimeError: If the image cleanup process fails.
        """

        prompt = f"""
        The goal is to remove the {asset_name} from the room image.
        
        Step 1: Identify the {asset_name}
            Identify the {asset_name} in the image and understand its surroundings. 
        
        Step 2: Remove the {asset_name}
            Remove the {asset_name} from the room. If there are any assets are attached to the {asset_name} also remove those.
            
        Step 3: Fill the gap
             Fill the gap that is left after you removed the {asset_name} in a way that the image looks natural and realistic, as if the {asset_name} was never there.
             Use the surroundings of the {asset_name} to fill the gap, so the style, lighting and texture of the original image is maintained as much as possible.

        Step 4: Verify
            Verify that the {asset_name} is completely removed and the image looks natural and realistic, as if the {asset_name} was never there. 
            Make sure you didn't change anything else in the image except removing the {asset_name} and filling the gap that is left after you removed the {asset_name}.
        
        Rules:
            - Make no changes to the other assets in the room
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
            print("Removed the {asset_name} from the image!")
            return response.parts[0].as_image()

        raise RuntimeError("image cleanup failed")


    def combine_images(self, room_image_with_missing_asset, asset_image, room_dimensions, asset_dimensions, location_orientation_asset):
        """
        Combines a room image with an asset image using a generative model.

        This method instructs a generative AI model to place a given asset (e.g., a sofa)
        into a room image. It uses detailed prompts that include dimensions, location,
        and orientation to ensure the asset is scaled and placed realistically.

        Args:
            room_image_with_missing_asset (Image): A PIL Image of the room where the asset will be placed.
            asset_image (Image): A PIL Image of the asset to place in the room.
            room_dimensions (str): A string describing the dimensions of existing assets in the room.
            asset_dimensions (str): A string describing the dimensions of the new asset.
            location_orientation_asset (str): A string describing the desired location and orientation of the new asset.

        Returns:
            Image: A new PIL Image object showing the room with the asset placed inside.

        Raises:
            LlmUnavailableError: If the call to the generative AI model fails.
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
            - Make no changes to the other assets in the room
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
                )
            )
        except exceptions.GoogleAPICallError:
            raise LlmUnavailableError("LLM API call failed")

        print("Afbeelding succesvol gegenereerd!")
        return response.parts[0].as_image()


    def get_asset_dimensions(self, room_image) -> str:
        """Estimates the dimensions of assets within an image.

        This method sends an image to a generative AI model to analyze and
        estimate the dimensions of all visible assets. The model is instructed
        to return the depth, width, height, and area for each asset in a
        specific format.

        Args:
            room_image (Image): A PIL Image object of the room containing assets.

        Returns:
            str: A formatted string listing each asset and its estimated dimensions in the format

            [asset-name-1]: area=[area], depth=[depth], width=[width], height=[height]
        """
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

    def get_asset_location_orientation(self, room_image, asset_name) -> str:
        """Determines the location and orientation of a in an image.

        This method sends an image to a generative AI model to describe the
        location and orientation of a specific asset (e.g., a sofa) within the room.
        The model is instructed to return the information in a structured format.

        Args:
            room_image (Image): A PIL Image object of the room containing the asset.
            asset_name (str): The name of the asset for which to determine location and orientation.

        Returns:
            str: A formatted string describing the asset's location and orientation.

            location: [location]

            orientation: [orientation]
        """
        prompt = f"""
        Describe the location and the orientation of the {asset_name} in the room.  
        Use this format:
            location: [location]
            orientation: [orientation]

        Rules:
            - location: Don't describe the form or design of the {asset_name}, just the place where the main part of the {asset_name} is located in relation to other assets. 
            - orientation: Don't describe the form or design of the {asset_name}, just where the sofa is oriented to, in relation to the viewer.
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
