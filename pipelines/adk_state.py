"""
ADK Pipeline State Management

Manages shared state across ADK workflow agents, including:
- Dataset accumulation
- Target count tracking
- Termination conditions
"""

from typing import Dict, List
from utils.logger import get_logger

logger = get_logger("adk_state")


class PipelineState:
    """
    Shared state for ADK pipeline execution.
    
    Tracks dataset progress and determines when to stop the loop.
    """
    
    def __init__(self, target_count: int, query: str):
        """
        Initialize pipeline state.
        
        Args:
            target_count: Target number of images to collect
            query: Object query for annotation
        """
        self.target_count = target_count
        self.query = query
        self.dataset = {}
        self.current_count = 0
        self.iteration = 0
        self.total_mined = 0
        self.total_curated = 0
        self.total_annotated = 0
        
        logger.info(f"Pipeline state initialized: target={target_count}, query='{query}'")
    
    def add_annotations(self, annotations: Dict) -> bool:
        """
        Add annotations to dataset.
        
        Args:
            annotations: Dictionary mapping filename to annotation data
            
        Returns:
            True if target count reached, False otherwise
        """
        added = 0
        for filename, data in annotations.items():
            if self.current_count < self.target_count:
                self.dataset[filename] = data
                self.current_count += 1
                added += 1
            else:
                break
        
        logger.info(f"Added {added} annotations. Progress: {self.current_count}/{self.target_count}")
        return self.should_stop()
    
    def should_stop(self) -> bool:
        """
        Check if pipeline should stop.
        
        Returns:
            True if target count reached, False otherwise
        """
        return self.current_count >= self.target_count
    
    def increment_iteration(self):
        """Increment iteration counter."""
        self.iteration += 1
        logger.debug(f"Iteration {self.iteration} started")
    
    def record_mining(self, count: int):
        """Record mining results."""
        self.total_mined += count
        logger.debug(f"Mining: +{count} images (total: {self.total_mined})")
    
    def record_curation(self, count: int):
        """Record curation results."""
        self.total_curated += count
        logger.debug(f"Curation: +{count} images (total: {self.total_curated})")
    
    def record_annotation(self, count: int):
        """Record annotation results."""
        self.total_annotated += count
        logger.debug(f"Annotation: +{count} images (total: {self.total_annotated})")
    
    def get_summary(self) -> Dict:
        """
        Get pipeline execution summary.
        
        Returns:
            Dictionary with execution statistics
        """
        return {
            "target": self.target_count,
            "collected": self.current_count,
            "iterations": self.iteration,
            "total_mined": self.total_mined,
            "total_curated": self.total_curated,
            "total_annotated": self.total_annotated,
            "success_rate": {
                "curation": f"{(self.total_curated / self.total_mined * 100):.1f}%" if self.total_mined > 0 else "N/A",
                "annotation": f"{(self.total_annotated / self.total_curated * 100):.1f}%" if self.total_curated > 0 else "N/A"
            }
        }
    
    def get_needed_count(self) -> int:
        """
        Get number of images still needed.
        
        Returns:
            Number of images needed to reach target
        """
        return max(0, self.target_count - self.current_count)
