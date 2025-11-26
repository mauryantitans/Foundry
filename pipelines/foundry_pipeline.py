"""
Foundry ADK Pipeline Implementation

This module defines the high-level pipeline orchestration using Google ADK.
It integrates the Miner, Curator, and Annotator agents into a cohesive workflow.
"""

import os
import time
from typing import Dict, List
from services.miner import MinerService
from services.curator import CuratorService
from services.annotator import AnnotatorService
from services.parallel_annotator import ParallelAnnotatorAgent
from services.engineer import EngineerService
from utils.logger import get_logger
from utils.pipeline_features import get_pipeline_features

logger = get_logger("adk_pipeline")


class FoundryPipeline:
    """
    Foundry dataset creation pipeline.
    
    Uses ADK workflow agents for orchestration:
    - SequentialAgent: Mine → Curate → Annotate
    - LoopAgent: Repeat until target reached
    """
    
    def __init__(self, query: str, target_count: int, annotation_query: str = None):
        """
        Initialize the Foundry pipeline.
        
        Args:
            query: Query for searching/mining images (e.g., 'dog' or 'person playing guitar')
            target_count: Target number of images to collect
            annotation_query: Query for annotation (e.g., 'dog,cat'). If None, uses query.
        """
        self.query = query  # For mining
        self.annotation_query = annotation_query or query  # For annotation
        self.target_count = target_count
        self.dataset = {}
        
        # Initialize agents (needed for tools)
        self._miner = MinerService()
        self._curator = CuratorService()
        self._annotator = AnnotatorService()
        
        # Get features
        self.features = get_pipeline_features()
        self.metrics = self.features.get_metrics() if self.features.enable_metrics else None
        
        logger.info(f"Foundry Pipeline initialized: query='{query}', target={target_count}")
    
    def run(self) -> Dict:
        """
        Execute the pipeline using ADK workflow agents.
        
        Returns:
            Dictionary with results and statistics
        """
        from pipelines.adk_state import PipelineState
        
        logger.info("="*70)
        logger.info("🚀 STARTING FOUNDRY PIPELINE (Fallback Mode)")
        logger.info("="*70)
        logger.info(f"Query: '{self.query}'")
        logger.info(f"Target: {self.target_count} images")
        logger.info(f"Architecture: Direct Sequential [Mine → Curate → Annotate]")
        logger.info("="*70)
        
        if self.metrics:
            self.metrics.start_pipeline()
        
        # Create pipeline state with annotation query
        state = PipelineState(target_count=self.target_count, query=self.annotation_query)
        
        try:
            logger.info("Running pipeline with direct tool calls...")
            
            # Import tools
            from services.miner import MinerService
            from services.curator import CuratorService
            from services.annotator import AnnotatorService
            
            miner = MinerService()
            curator = CuratorService()
            annotator = AnnotatorService()
            
            max_iterations = 20
            iteration = 0
            
            while not state.should_stop() and iteration < max_iterations:
                iteration += 1
                state.increment_iteration()
                
                logger.info(f"\n{'='*70}")
                logger.info(f"Iteration {iteration} - Need {state.get_needed_count()} more images")
                logger.info(f"{'='*70}")
                
                # Mine
                logger.info("1️⃣  Mining images...")
                needed = state.get_needed_count() * 2  # Request 2x to account for filtering
                
                # Track mining time
                mine_start = time.time()
                mine_result = miner.mine(self.query, needed)
                mine_time = time.time() - mine_start
                
                # Extract paths from result dictionary
                if mine_result["status"] == "success":
                    mined_paths = mine_result["data"]
                else:
                    mined_paths = []
                
                state.record_mining(len(mined_paths))
                if self.metrics:
                    self.metrics.record_mining(attempted=needed, successful=len(mined_paths), time_taken=mine_time)
                logger.info(f"   ✓ Mined {len(mined_paths)} images")
                
                if not mined_paths:
                    logger.warning("   ⚠ No images mined, stopping")
                    break
                
                # Curate
                logger.info("2️⃣  Curating images...")
                curate_start = time.time()
                curated_paths = curator.curate(self.query, mined_paths)
                curate_time = time.time() - curate_start
                
                state.record_curation(len(curated_paths))
                if self.metrics:
                    self.metrics.record_curation(total=len(mined_paths), kept=len(curated_paths), time_taken=curate_time)
                logger.info(f"   ✓ Curated {len(curated_paths)} images")
                
                if not curated_paths:
                    logger.warning("   ⚠ No images passed curation, stopping")
                    break
                
                # Annotate
                logger.info("3️⃣  Annotating images...")
                annotate_start = time.time()
                annotations = annotator.annotate(self.annotation_query, curated_paths)
                annotate_time = time.time() - annotate_start
                
                state.record_annotation(len(annotations))
                if self.metrics:
                    self.metrics.record_annotation(total=len(curated_paths), successful=len(annotations), time_taken=annotate_time)
                logger.info(f"   ✓ Annotated {len(annotations)} images")
                
                if not annotations:
                    logger.warning("   ⚠ No annotations generated, stopping")
                    break
                
                # Add to dataset
                should_stop = state.add_annotations(annotations)
                logger.info(f"   📊 Progress: {state.current_count}/{state.target_count}")
                
                if should_stop:
                    logger.info(f"   ✅ Target reached!")
                    break
            
            logger.info(f"\nPipeline completed in {iteration} iterations")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            # Continue with whatever we have
            pass
        
        # Use the state's dataset
        self.dataset = state.dataset
        
        # Save dataset
        output_path = None
        if self.dataset:
            output_path = self._save_dataset()
        
        if self.metrics:
            self.metrics.end_pipeline()
        
        # Final summary
        summary = state.get_summary()
        logger.info("="*70)
        logger.info("✅ PIPELINE COMPLETED")
        logger.info("="*70)
        logger.info(f"Status: Success")
        logger.info(f"Images Collected: {summary['collected']}/{summary['target']}")
        logger.info(f"Iterations: {summary['iterations']}")
        logger.info(f"Total Mined: {summary['total_mined']}")
        logger.info(f"Total Curated: {summary['total_curated']}")
        logger.info(f"Total Annotated: {summary['total_annotated']}")
        if output_path:
            logger.info(f"Output: {output_path}")
        logger.info("="*70)
        
        return {
            "status": "success",
            "images_collected": len(self.dataset),
            "target": self.target_count,
            "iterations": summary['iterations'],
            "output_path": output_path,
            "dataset": self.dataset,
            "adk_mode": True
        }
    
    def _save_dataset(self) -> str:
        """Save dataset to COCO format."""
        logger.info(f"💾 Saving dataset with {len(self.dataset)} images...")
        
        start_time = time.time()
        engineer = EngineerService(query=self.annotation_query)  # Use annotation query for categories
        
        for filename, data in self.dataset.items():
            engineer.process_item(filename, data)
        
        output_path = engineer.save()
        elapsed = time.time() - start_time
        
        if self.metrics:
            self.metrics.record_engineering(count=len(self.dataset), time_taken=elapsed)
        
        logger.info(f"✅ Dataset saved to: {output_path}")
        return output_path


class FoundryBYODPipeline:
    """BYOD mode: Annotate existing images."""
    
    def __init__(self, image_dir: str, query: str):
        self.image_dir = image_dir
        self.query = query
        self._annotator = AnnotatorService()
        
        self.features = get_pipeline_features()
        self.metrics = self.features.get_metrics() if self.features.enable_metrics else None
        
        self.quality_loop = None
        if self.features.enable_quality_loop:
            self.quality_loop = self.features.create_quality_loop(self._annotator)
        
        self.parallel_annotator = ParallelAnnotatorAgent(
            num_workers=3,
            quality_loop=self.quality_loop
        )
    
    def run(self) -> Dict:
        """Execute BYOD pipeline."""
        from utils.file_manager import list_images
        
        logger.info("="*70)
        logger.info("📁 BYOD MODE - Annotating Your Images")
        logger.info("="*70)
        logger.info(f"Directory: {self.image_dir}")
        logger.info(f"Query: {self.query}")
        logger.info("="*70)
        
        if self.metrics:
            self.metrics.start_pipeline()
        
        # Get images
        image_paths = list_images(self.image_dir)
        if not image_paths:
            logger.error(f"No images found in {self.image_dir}")
            return {"status": "error", "message": "No images found"}
        
        logger.info(f"Found {len(image_paths)} images")
        
        # Annotate
        start_time = time.time()
        if len(image_paths) > 1:
            annotations = self.parallel_annotator.annotate_parallel(self.query, image_paths)
        else:
            annotations = self._annotator.annotate(self.query, image_paths)
        elapsed = time.time() - start_time
        
        if self.metrics:
            self.metrics.record_annotation(total=len(image_paths), successful=len(annotations), time_taken=elapsed)
        
        if not annotations:
            logger.error("No annotations generated")
            return {"status": "error", "message": "Annotation failed"}
        
        # Save
        start_time = time.time()
        engineer = EngineerService(query=self.query)
        for filename, data in annotations.items():
            engineer.process_item(filename, data)
        output_path = engineer.save()
        elapsed = time.time() - start_time
        
        if self.metrics:
            self.metrics.record_engineering(count=len(annotations), time_taken=elapsed)
            self.metrics.end_pipeline()
        
        logger.info("="*70)
        logger.info("✅ BYOD MODE COMPLETED")
        logger.info(f"Annotated: {len(annotations)} images")
        logger.info(f"Output: {output_path}")
        logger.info("="*70)
        
        return {
            "status": "success",
            "images_annotated": len(annotations),
            "output_path": output_path
        }
