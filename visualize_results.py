import json
import os
from PIL import Image, ImageDraw

def visualize_coco(coco_path, image_dir, output_dir):
    with open(coco_path, 'r') as f:
        data = json.load(f)
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Map image_id to filename
    image_map = {img['id']: img['file_name'] for img in data['images']}
    
    # Group annotations by image_id
    annotations = {}
    for ann in data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations:
            annotations[img_id] = []
        annotations[img_id].append(ann['bbox'])
        
    for img_id, bboxes in annotations.items():
        filename = image_map.get(img_id)
        if not filename:
            continue
            
        img_path = os.path.join(image_dir, filename)
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue
            
        try:
            image = Image.open(img_path)
            draw = ImageDraw.Draw(image)
            
            for bbox in bboxes:
                # COCO bbox is [x, y, width, height]
                x, y, w, h = bbox
                draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
                
            save_path = os.path.join(output_dir, f"vis_{filename}")
            image.save(save_path)
            print(f"Saved visualization to {save_path}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    visualize_coco(
        "data/output/coco.json",
        "data/curated",
        "data/debug"
    )
