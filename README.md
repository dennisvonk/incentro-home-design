# Home Design

A small PoC in Python that does image replacements using LLMs. The goal is to replace any asset in the room by another asset of the same type. The resulting image should give a user a good impression on how the new asset will look like in the room.

## Project Structuur
- `src/`: Bevat de broncode.
- `tests/`: Bevat de unit tests.

## Testen
In order to run the tests & the application, you must have Python 3.8 or higher installed. You can install the required dependencies with:
```bash
pip install -r requirements.txt
```
Also you need to set up your API keys for the AI services you intend to use (e.g., Google Gemini, Claude). Make sure to set these keys in a `.env`-file and use this file when testing. There is an example `.env.example` file provided to guide you in setting up your environment variables.

You can use the capabilities of an IDE like IntelliJ IDEA or run the tests from the command line with:
```bash
pytest
```
"TODO" find out how to add the `.env` file when running the tests from the CLI.


## TODO
- get and test multiple rooms and sofas
- programmeren met langgraph
- size of the output image same as the input image
- use claude code, setup api key
- set google gemini api key in environment variable
- create fast-api endpoints to handle the requests
- create a frontend interface
- how to handle an empty room

## Brainstorm
- research client.chats.create (https://ai.google.dev/gemini-api/docs/image-generation#multi-turn-image-editing)
- add image_config (https://ai.google.dev/gemini-api/docs/image-generation#use-14-images)
- foto's van collega's vragen
- render a 3d model of the room based on the input specifications.
  - Top AI 3D Model Generators (2026)The following platforms allow you to describe or upload an object and download a functional 3D file:ToolKey FeaturesExport FormatsTripo AIHighly rated in 2026 for speed and "watertight" meshes suitable for 3D printing..obj, .stl, .glb, .fbxMeshy AIA "multimodal powerhouse" that supports text-to-3D and image-to-3D with AI texturing..obj, .stl, .fbx, .glb, .blend3D AI StudioFocuses on production-ready assets with clean topology and PBR textures..obj, .stl, .fbx, .glb, .3mfRodin (Hyper3D)Specializes in high-fidelity 3D assets with clean topology for game development..obj, .glb, .fbxSloydUses a library of customizable templates to generate precise, editable 3D models.Compatible with major 3D software
