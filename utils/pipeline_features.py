"""
Advanced pipeline features integration module.

This module provides:
- Metrics Collection: Track performance, success rates, and timing
- Quality Refinement: Iterative annotation improvement
- Error Handling: Structured error management
"""
from utils.metrics import get_metrics_collector
from agents.quality_loop import AnnotationRefinementLoop
from utils.error_handler import ErrorHandler, create_error_response, create_success_response
from utils.logger import get_logger

logger = get_logger("features")

class PipelineFeatures:
    """
    Advanced pipeline features manager.
    Handles metrics collection, quality loops, and error management.
    """
    
    def __init__(
        self, 
        enable_metrics: bool = True,
        enable_quality_loop: bool = False,  # Optional, adds processing time
        quality_loop_iterations: int = 2
    ):
        """
        Initialize pipeline features.
        
        Args:
            enable_metrics: Enable metrics collection
            enable_quality_loop: Enable quality refinement loop
            quality_loop_iterations: Max iterations for quality loop
        """
        self.enable_metrics = enable_metrics
        self.enable_quality_loop = enable_quality_loop
        self.quality_loop_iterations = quality_loop_iterations
        
        # Initialize components
        self.metrics = get_metrics_collector() if enable_metrics else None
        self.quality_loop = None  # Will be initialized when needed
        
        logger.info(f"Pipeline Features initialized:")
        logger.info(f"  - Metrics Collection: {'✅ Enabled' if enable_metrics else '❌ Disabled'}")
        logger.info(f"  - Quality Loop: {'✅ Enabled' if enable_quality_loop else '❌ Disabled'}")
        if enable_quality_loop:
            logger.info(f"    → Max iterations: {quality_loop_iterations}")
    
    def create_quality_loop(self, annotator_agent):
        """Create quality refinement loop instance."""
        if self.enable_quality_loop and not self.quality_loop:
            self.quality_loop = AnnotationRefinementLoop(
                annotator_agent=annotator_agent,
                max_iterations=self.quality_loop_iterations
            )
            logger.info("Quality refinement loop created")
        return self.quality_loop
    
    def get_metrics(self):
        """Get metrics collector instance."""
        return self.metrics
    
    def print_metrics_summary(self):
        """Print metrics summary if metrics are enabled."""
        if self.metrics:
            self.metrics.print_summary()
        else:
            logger.info("Metrics collection is disabled")

# Global instance
_features_instance = None

def initialize_pipeline_features(
    enable_metrics: bool = True,
    enable_quality_loop: bool = False,
    quality_loop_iterations: int = 2
) -> PipelineFeatures:
    """
    Initialize pipeline features globally.
    
    Args:
        enable_metrics: Enable metrics collection
        enable_quality_loop: Enable quality refinement loop
        quality_loop_iterations: Max iterations for quality loop
        
    Returns:
        PipelineFeatures instance
    """
    global _features_instance
    _features_instance = PipelineFeatures(
        enable_metrics=enable_metrics,
        enable_quality_loop=enable_quality_loop,
        quality_loop_iterations=quality_loop_iterations
    )
    return _features_instance

def get_pipeline_features() -> PipelineFeatures:
    """Get global PipelineFeatures instance."""
    global _features_instance
    if _features_instance is None:
        _features_instance = PipelineFeatures()
    return _features_instance
