import asyncio
import json
import base64
import httpx
from pathlib import Path
from PIL import Image
import io
import os
import glob

os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

def encode_and_compress_image(image_path: Path, max_dimension: int = 1024, quality: int = 85) -> str:
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
            
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int((max_dimension / width) * height)
            else:
                new_height = max_dimension
                new_width = int((max_dimension / height) * width)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

async def test():
    # Use a dummy image if no frame is found
    frames = glob.glob("data/frames/**/*.jpg", recursive=True)
    if not frames:
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save('C:/Mukul K/vinfo1/video-search-engine/dummy.jpg')
        image_path = Path('C:/Mukul K/vinfo1/video-search-engine/dummy.jpg')
    else:
        image_path = Path(frames[0])

    print(f"Using image: {image_path}")
    base64_image = encode_and_compress_image(image_path)
    print(f"Compressed image size = {len(base64_image)}")

    payload = {
        "model": "qwen3-vl:8b",
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON-only vision analysis assistant. Respond ONLY with a valid JSON object matching the requested schema. No markdown, no commentary, no <think> blocks."
            },
            {
                "role": "user",
                "content": "Describe the image.",
                "images": [base64_image],
            }
        ],
        "format": "json",
        "stream": False,
        "options": {
            "num_predict": 4096,
            "temperature": 0.0,
        }
    }
    
    print("OLLAMA PAYLOAD SCHEMA:")
    payload_copy = json.loads(json.dumps(payload))
    payload_copy["messages"][1]["images"] = ["<base64_string_length_" + str(len(base64_image)) + ">"]
    print(json.dumps(payload_copy, indent=2))
    
    async with httpx.AsyncClient() as client:
        print("Sending request to Ollama WITH format=json...")
        response = await client.post("http://127.0.0.1:11434/api/chat", json=payload, timeout=60.0)
        print(f"STATUS={response.status_code}")
        print(response.text)
        
        print("\nSending request to Ollama WITHOUT format=json...")
        payload_no_json = json.loads(json.dumps(payload))
        del payload_no_json["format"]
        response2 = await client.post("http://127.0.0.1:11434/api/chat", json=payload_no_json, timeout=60.0)
        print(f"STATUS={response2.status_code}")
        print(response2.text)

if __name__ == "__main__":
    asyncio.run(test())
