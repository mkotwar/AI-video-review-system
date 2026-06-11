import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_pipeline():
    # 1. Ask for a video file or check if one exists
    if len(sys.argv) > 1:
        video_path = sys.argv[1].strip()
    else:
        video_path = input("Enter path to a test video file (.mp4, .avi, or .mov): ").strip()
        
    # Strip surrounding quotes if present
    if (video_path.startswith('"') and video_path.endswith('"')) or (video_path.startswith("'") and video_path.endswith("'")):
        video_path = video_path[1:-1].strip()
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' does not exist.")
        return

    print(f"\n--- Step 1: Uploading video '{os.path.basename(video_path)}' ---")
    upload_url = f"{BASE_URL}/videos/upload"
    with open(video_path, "rb") as f:
        files = {"file": (os.path.basename(video_path), f, "video/mp4")}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 201:
        print(f"Upload failed (Status Code {response.status_code}): {response.text}")
        return
        
    metadata = response.json()
    video_id = metadata["video_id"]
    print(f"Upload Success! Video ID: {video_id}")
    print(f"Uploaded Details: {metadata}")

    print(f"\n--- Step 2: Extracting frames & generating AI VLM metadata ---")
    print("NOTE: On the first run, the model weights (approx. 14GB) will be downloaded from Hugging Face.")
    print("This might take a few minutes. Please wait...")
    
    extract_url = f"{BASE_URL}/frames/extract"
    payload = {"video_id": video_id}
    
    start_time = time.time()
    response = requests.post(extract_url, json=payload)
    duration = time.time() - start_time
    
    if response.status_code != 200:
        print(f"Extraction failed (Status Code {response.status_code}): {response.text}")
        return

    result = response.json()
    print(f"\nExtraction completed in {duration:.2f} seconds!")
    print(f"Processed Frames: {result['processed_frames']}")
    print(f"Successful Frames: {result['successful_frames']}")
    print(f"Failed Frames: {result['failed_frames']}")

    print(f"\n--- Step 3: Checking metadata quality ---")
    frames = result["frames"]
    if not frames:
        print("No frames were successfully processed by the VLM.")
        return

    for idx, frame in enumerate(frames):
        print(f"\n[Frame {idx+1}] - Timestamp: {frame['timestamp_human']} ({frame['timestamp_seconds']}s)")
        print(f"  • Caption: {frame['caption']}")
        print(f"  • Scene Type: {frame['scene_type']}")
        print(f"  • Scene Description: {frame['scene_description']}")
        print(f"  • People Count: {frame['people_count']}")
        print(f"  • Activities: {', '.join(frame['activities'])}")
        print(f"  • Keywords: {', '.join(frame['keywords'])}")
        if frame["objects"]:
            print("  • Detected Objects:")
            for obj in frame["objects"]:
                print(f"    - {obj['color']} {obj['subtype']} ({obj['type']}) | Attributes: {', '.join(obj['attributes'])}")
        print(f"  • Unified Search Text: '{frame['search_text']}'")

if __name__ == "__main__":
    # Ensure requests library is installed
    try:
        import requests
    except ImportError:
        print("Installing requests library for testing...")
        os.system("pip install requests")
        import requests
    test_pipeline()
