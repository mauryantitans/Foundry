from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from services.annotator import AnnotatorService
from utils.logger import get_logger

logger = get_logger("parallel_annotator")

class ParallelAnnotatorAgent:
    """
    Manages parallel execution of annotation tasks.
    """
    
    def __init__(self, num_workers: int = 3, quality_loop = None):
        self.num_workers = num_workers
        self.quality_loop = quality_loop
        self.service = AnnotatorService()

    def annotate_parallel(self, query: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        Annotates images in parallel using ThreadPoolExecutor.
        """
        logger.info(f"🚀 Starting parallel annotation with {self.num_workers} workers for {len(image_paths)} images")
        
        results = {}
        
        # Helper function for a single task
        def annotate_single(path):
            # AnnotatorService.annotate expects a list of paths and returns a dict
            return self.service.annotate(query, [path])

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_path = {executor.submit(annotate_single, path): path for path in image_paths}
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    annotation = future.result()
                    if annotation:
                        # If quality loop is enabled, verify the annotation
                        if self.quality_loop:
                            # Extract the single item from the dict
                            filename = list(annotation.keys())[0]
                            data = annotation[filename]
                            
                            # Verify
                            is_valid, feedback = self.quality_loop.verify_annotation(path, data["bboxes"], query)
                            
                            if is_valid:
                                results.update(annotation)
                            else:
                                filename = list(annotation.keys())[0]
                                logger.warning(f"Quality Loop rejected {filename}: {feedback}")
                        else:
                            results.update(annotation)
                            
                except Exception as e:
                    logger.error(f"Worker failed for {path}: {e}")
        
        return results
