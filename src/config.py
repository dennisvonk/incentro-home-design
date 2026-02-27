"""
Configuration settings for the application.
"""
import os

RESOURCE_FOLDER = "tests\\resources"

class Configuration:
    _asset_path: str
    _room_path: str
    output_path: str

    # LLM configuration
    """
    These are the different Nano Banana model available! :
    - models/nano-banana-pro-preview - Display name: "Nano Banana Pro". Supported actions: generateContent, countTokens, batchGenerateContent
    - models/gemini-3-pro-image-preview - Display name: "Nano Banana Pro". Supported actions: generateContent, countTokens, batchGenerateContent
    - models/gemini-2.5-flash-image - Display name: "Nano Banana". Supported actions: generateContent, countTokens, batchGenerateContent
    """
    llm_model_name_image_processing = "models/nano-banana-pro-preview"     # hardcoded for now
    llm_model_name_dimensions = "gemini-2.5-flash-image"          # hardcoded for now
    llm_api_key = os.getenv("LLM_API_KEY")

    def __init__(self, resources_test_path: str):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to project root (since script is in src/)
        project_root = os.path.dirname(script_dir)

        # Use provided path or default to resources in project root
        resources_path = os.path.join (RESOURCE_FOLDER, resources_test_path)
        full_resources_path = resources_path if os.path.isabs(resources_path) else os.path.join(project_root, resources_path)

        print(f"Using resources path: {full_resources_path}")
        self._asset_path = os.path.join(full_resources_path, "input", "asset")
        self._room_path = os.path.join(full_resources_path, "input", "room")

        self.output_path = os.path.join(full_resources_path, "output")


    def get_asset_image_path(self, name: str) -> str:
        return os.path.join(self._asset_path, f"{name}")


    def get_room_image_path(self, name: str) -> str:
        return os.path.join(self._room_path, f"{name}")
