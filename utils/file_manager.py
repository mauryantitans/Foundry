import os
import requests
from PIL import Image
from io import BytesIO
import hashlib

def create_directories(base_path):
    """Creates the necessary directories for the project."""
    dirs = ['data/raw', 'data/curated', 'data/debug', 'data/output']
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)

def save_image(url, save_folder):
    """Downloads and saves an image from a URL. Returns the file path or None."""
    try:
        # Ensure directory exists
        os.makedirs(save_folder, exist_ok=True)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Verify it's an image
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Generate a unique filename based on content hash
        file_hash = hashlib.md5(response.content).hexdigest()
        filename = f"{file_hash}.jpg"
        file_path = os.path.join(save_folder, filename)
        
        image.save(file_path, "JPEG", quality=85)
        return file_path
    except Exception as e:
        # print(f"Failed to download {url}: {e}")
        return None

def list_images(folder_path):
    """Returns a list of image paths in a folder."""
    if not os.path.exists(folder_path):
        return []
    valid_exts = ['.jpg', '.jpeg', '.png']
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
            if os.path.splitext(f)[1].lower() in valid_exts]
