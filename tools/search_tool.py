import os
from googleapiclient.discovery import build

def google_search_images(query: str, num_images: int = 5, start_index: int = 1):
    """
    Searches for images using Google Custom Search API.
    
    Args:
        query: The search query for images.
        num_images: The number of images to return (max 10 per call, will loop if needed).
        start_index: The starting index for the search results (1-based).
        
    Returns:
        A list of image URLs.
    """
    num_images = int(num_images)
    start_index = int(start_index)
    print(f"🔍 Search Tool: Searching for {num_images} images of '{query}' starting at {start_index}...")
    
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if not api_key or not cx:
        print("❌ Error: GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX not found.")
        return []

    service = build("customsearch", "v1", developerKey=api_key)
    
    image_urls = []
    start_index = 1
    
    # Cap at a reasonable number for this tool to avoid excessive API usage in loops
    # The user can request more, but we'll handle pagination.
    
    while len(image_urls) < num_images:
        try:
            # Google Custom Search allows max 10 results per page
            fetch_num = min(10, num_images - len(image_urls))
            
            res = service.cse().list(
                q=query,
                cx=cx,
                searchType="image",
                num=fetch_num, 
                start=start_index,
                safe="off"
            ).execute()
            
            items = res.get("items", [])
            if not items:
                print("   ⚠️ No more results found.")
                break
                
            for item in items:
                link = item.get("link")
                if link:
                    image_urls.append(link)
            
            start_index += len(items)
            
            if len(items) < fetch_num:
                break
                
        except Exception as e:
            print(f"   ❌ Google Search Error: {e}")
            break

    print(f"   Found {len(image_urls)} images.")
    return image_urls[:num_images]
