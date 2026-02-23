# Home Design

Een klein Python project voor het vervangen van objecten in een kamer.

## Project Structuur
- `src/`: Bevat de broncode.
- `tests/`: Bevat de unit tests.

## Dependencies
```bash
pip install pytest
pip install -U google-generativeai
```

## Testen
You can use the capabilities of an IDE like IntelliJ IDEA or run the tests from the command line with:
```bash
pytest
```

## Brainstorm
- research client.chats.create (https://ai.google.dev/gemini-api/docs/image-generation#multi-turn-image-editing)
- add image_config (https://ai.google.dev/gemini-api/docs/image-generation#use-14-images)
- programmeren met langchain en/of langgraph
- foto's van collega's vragen
- render a 3d model of the room based on the input specifications.
  - Top AI 3D Model Generators (2026)The following platforms allow you to describe or upload an object and download a functional 3D file:ToolKey FeaturesExport FormatsTripo AIHighly rated in 2026 for speed and "watertight" meshes suitable for 3D printing..obj, .stl, .glb, .fbxMeshy AIA "multimodal powerhouse" that supports text-to-3D and image-to-3D with AI texturing..obj, .stl, .fbx, .glb, .blend3D AI StudioFocuses on production-ready assets with clean topology and PBR textures..obj, .stl, .fbx, .glb, .3mfRodin (Hyper3D)Specializes in high-fidelity 3D assets with clean topology for game development..obj, .glb, .fbxSloydUses a library of customizable templates to generate precise, editable 3D models.Compatible with major 3D software
