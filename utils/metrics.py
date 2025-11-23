"""
Metrics collection system for tracking pipeline performance.
"""
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger("metrics")

class MetricsCollector:
    """
    Collects and tracks metrics throughout the pipeline execution.
    """
    
    def __init__(self):
        self.metrics = {
            "pipeline_runs": 0,
            "images_mined": 0,
            "images_curated": 0,
            "images_annotated": 0,
            "images_saved": 0,
            "curation_success_rate": [],
            "annotation_success_rate": [],
            "timings": defaultdict(list),
            "errors": defaultdict(int),
            "start_time": None,
            "end_time": None
        }
        self.current_run = {}
        
    def start_pipeline(self):
        """Start tracking a new pipeline run."""
        self.metrics["pipeline_runs"] += 1
        self.metrics["start_time"] = datetime.now()
        self.current_run = {
            "start_time": time.time(),
            "stages": {}
        }
        logger.info("📊 Started metrics collection for pipeline run")
        
    def end_pipeline(self):
        """End tracking current pipeline run."""
        self.metrics["end_time"] = datetime.now()
        if self.current_run:
            total_time = time.time() - self.current_run["start_time"]
            self.metrics["timings"]["pipeline_total"].append(total_time)
            logger.info(f"📊 Pipeline completed in {total_time:.2f}s")
            
    def start_stage(self, stage_name: str):
        """Start tracking a pipeline stage."""
        self.current_run["stages"][stage_name] = {
            "start_time": time.time()
        }
        
    def end_stage(self, stage_name: str, success: bool = True, count: int = 0):
        """End tracking a pipeline stage."""
        if stage_name in self.current_run["stages"]:
            elapsed = time.time() - self.current_run["stages"][stage_name]["start_time"]
            self.metrics["timings"][stage_name].append(elapsed)
            self.current_run["stages"][stage_name]["elapsed"] = elapsed
            self.current_run["stages"][stage_name]["success"] = success
            self.current_run["stages"][stage_name]["count"] = count
            
    def record_mining(self, attempted: int, successful: int, time_taken: float):
        """Record mining metrics."""
        self.metrics["images_mined"] += successful
        self.metrics["timings"]["mining"].append(time_taken)
        logger.debug(f"📊 Mining: {successful}/{attempted} images in {time_taken:.2f}s")
        
    def record_curation(self, total: int, kept: int, time_taken: float):
        """Record curation metrics."""
        self.metrics["images_curated"] += kept
        rate = (kept / total * 100) if total > 0 else 0
        self.metrics["curation_success_rate"].append(rate)
        self.metrics["timings"]["curation"].append(time_taken)
        logger.debug(f"📊 Curation: {kept}/{total} images ({rate:.1f}%) in {time_taken:.2f}s")
        
    def record_annotation(self, total: int, successful: int, time_taken: float):
        """Record annotation metrics."""
        self.metrics["images_annotated"] += successful
        rate = (successful / total * 100) if total > 0 else 0
        self.metrics["annotation_success_rate"].append(rate)
        self.metrics["timings"]["annotation"].append(time_taken)
        logger.debug(f"📊 Annotation: {successful}/{total} images ({rate:.1f}%) in {time_taken:.2f}s")
        
    def record_engineering(self, count: int, time_taken: float):
        """Record engineering/save metrics."""
        self.metrics["images_saved"] += count
        self.metrics["timings"]["engineering"].append(time_taken)
        logger.debug(f"📊 Engineering: {count} images in {time_taken:.2f}s")
        
    def record_error(self, stage: str, error_type: str):
        """Record an error occurrence."""
        key = f"{stage}_{error_type}"
        self.metrics["errors"][key] += 1
        
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        def avg(values: List[float]) -> float:
            return sum(values) / len(values) if values else 0.0
            
        summary = {
            "overview": {
                "pipeline_runs": self.metrics["pipeline_runs"],
                "total_images_mined": self.metrics["images_mined"],
                "total_images_curated": self.metrics["images_curated"],
                "total_images_annotated": self.metrics["images_annotated"],
                "total_images_saved": self.metrics["images_saved"]
            },
            "success_rates": {
                "curation_avg": f"{avg(self.metrics['curation_success_rate']):.1f}%",
                "annotation_avg": f"{avg(self.metrics['annotation_success_rate']):.1f}%"
            },
            "timings": {
                stage: {
                    "avg": f"{avg(times):.2f}s",
                    "total": f"{sum(times):.2f}s",
                    "count": len(times)
                }
                for stage, times in self.metrics["timings"].items()
            },
            "errors": dict(self.metrics["errors"]) if self.metrics["errors"] else "None"
        }
        
        return summary
        
    def print_summary(self):
        """Print formatted metrics summary."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 PIPELINE METRICS SUMMARY")
        print("="*60)
        
        print("\n📈 Overview:")
        for key, value in summary["overview"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
            
        print("\n✅ Success Rates:")
        for key, value in summary["success_rates"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
            
        print("\n⏱️  Average Timings:")
        for stage, timing in summary["timings"].items():
            print(f"   {stage.replace('_', ' ').title()}: {timing['avg']} ({timing['count']} runs)")
            
        if summary["errors"] != "None":
            print("\n❌ Errors:")
            for error, count in summary["errors"].items():
                print(f"   {error}: {count}")
        else:
            print("\n✅ No errors recorded")
            
        print("="*60 + "\n")
        
    def reset(self):
        """Reset all metrics."""
        self.__init__()
        logger.info("📊 Metrics reset")

# Global metrics instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
