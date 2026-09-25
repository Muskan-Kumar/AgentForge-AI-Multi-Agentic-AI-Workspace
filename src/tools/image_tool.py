from pathlib import Path
from uuid import uuid4

from huggingface_hub import InferenceClient
from langchain_core.tools import tool

from src.core.config import settings


IMAGE_OUTPUT_DIR = Path("generated/images")
IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



@tool
def image_tool(prompt: str)->str:
    """
    Generate an image from a natural-language prompt.

    Args:
        prompt: Detailed description of the image to generate.

    Returns:
        Path to the generated image.
    """

    if not prompt or not prompt.strip():
        return "Image generation failed: Prompt cannot be empty"

    try:
        client = InferenceClient(
            api_key=settings.HF_TOKEN
        )

        image = client.text_to_image(
            prompt=prompt.strip(),
            model=settings.IMAGE_MODEL,
        )

        file_name = f"{uuid4().hex}.png"
        output_path = IMAGE_OUTPUT_DIR / file_name

        image.save(output_path)

        return(
            "Image generation successfully.\n"
            f"File: {output_path.resolve()}"
        )
    
    except Exception as e:
        return f"Image generation errpr: {str(e)}"
    