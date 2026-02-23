from src.config import Configuration, RESOURCE_FOLDER
from src.image_processor import ImageProcessor
from src.llm_client import LlmClient

if __name__ == "__main__":
    config = Configuration(RESOURCE_FOLDER + "\\test-1")
    client = LlmClient(config)
    processor = ImageProcessor(config, client)
    image_with_new_furniture = processor.insert_furniture_into_room("meubel.webp", "kamer.jpg")
