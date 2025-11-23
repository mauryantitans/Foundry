import os
from googleapiclient.discovery import build

def google_search_images(query: str, num_images: int = 5, start_index: int = 1) -> dict:
    """
    Searches for images using Google Custom Search API.
    
    Args:
        query: The search query for images.
        num_images: The number of images to return (max 10 per call, will loop if needed).
        start_index: The starting index for the search results (1-based).
        
    Returns:
        Dictionary with status and data:
        Success: {"status": "success", "data": [...], "count": 5, "next_index": 6}
        Error: {"status": "error", "error_message": "...", "data": [], "count": 0}
    """
    import logging
    logger = logging.getLogger("foundry.search_tool")
    
    num_images = int(num_images)
    start_index = int(start_index)
    logger.info(f"Searching for {num_images} images of '{query}' starting at {start_index}")
    
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if not api_key or not cx:
        error_msg = "GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX not found"
        logger.error(error_msg)
        return {
            "status": "error",
            "error_message": error_msg,
            "data": [],
            "count": 0,
            "next_index": start_index
        }

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        
        image_urls = []
        current_index = start_index
        
        # Cap at a reasonable number for this tool to avoid excessive API usage in loops
        while len(image_urls) < num_images:
            try:
                # Google Custom Search allows max 10 results per page
                fetch_num = min(10, num_images - len(image_urls))
                
                res = service.cse().list(
                    q=query,
                    cx=cx,
                    searchType="image",
                    num=fetch_num, 
                    start=current_index,
                    safe="off"
                ).execute()
                
                items = res.get("items", [])
                if not items:
                    logger.warning("No more results found")
                    break
                    
                for item in items:
                    link = item.get("link")
                    if link:
                        image_urls.append(link)
                
                current_index += len(items)
                
                if len(items) < fetch_num:
                    break
                    
            except Exception as e:
                logger.error(f"Google Search API error: {e}")
                break

        result_urls = image_urls[:num_images]
        logger.info(f"Found {len(result_urls)} images")
        
        return {
            "status": "success",
            "data": result_urls,
            "count": len(result_urls),
            "next_index": current_index
        }
        
    except Exception as e:
        error_msg = f"Failed to search images: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error_message": error_msg,
            "data": [],
            "count": 0,
            "next_index": start_index
        }
