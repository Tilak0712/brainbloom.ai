from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from io import BytesIO

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def describe_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption
