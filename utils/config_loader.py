"""
Configuration loader for Foundry pipeline.
Supports YAML config files with CLI argument overrides.
"""
import yaml
import os
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("config")

class Config:
    """Configuration manager for Foundry pipeline."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML config file (optional)
        """
        self.config = self._load_default_config()
        
        if config_path:
            if os.path.exists(config_path):
                self._load_from_file(config_path)
                logger.info(f"📋 Loaded configuration from: {config_path}")
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'pipeline': {
                'query': None,
                'count': 5,
                'mode': 'standard',
                'image_dir': None
            },
            'quality_loop': {
                'enabled': False,
                'max_iterations': 2,
                'validation_method': 'coordinate'
            },
            'annotation': {
                'num_workers': 3
            },
            'metrics': {
                'enabled': True,
                'show_summary': False
            },
            'advanced': {
                'max_pipeline_loops': 5,
                'log_level': 'INFO'
            }
        }
    
    def _load_from_file(self, config_path: str):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
            
            if file_config:
                # Deep merge with defaults
                self._deep_merge(self.config, file_config)
                logger.debug(f"Merged config from file: {config_path}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge update dict into base dict."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def override_from_args(self, args):
        """
        Override config with CLI arguments.
        CLI args take precedence over config file.
        
        Args:
            args: argparse.Namespace with CLI arguments
        """
        # Pipeline settings
        if hasattr(args, 'query') and args.query:
            self.config['pipeline']['query'] = args.query
            logger.debug(f"CLI override: query = {args.query}")
        
        if hasattr(args, 'count') and args.count:
            self.config['pipeline']['count'] = args.count
            logger.debug(f"CLI override: count = {args.count}")
        
        if hasattr(args, 'request') and args.request:
            # Natural language request takes precedence
            self.config['pipeline']['request'] = args.request
            logger.debug(f"CLI override: request = {args.request}")
        
        if hasattr(args, 'dir') and args.dir:
            self.config['pipeline']['mode'] = 'byod'
            self.config['pipeline']['image_dir'] = args.dir
            logger.debug(f"CLI override: BYOD mode with dir = {args.dir}")
        
        # Quality loop settings
        if hasattr(args, 'enable_quality_loop') and args.enable_quality_loop:
            self.config['quality_loop']['enabled'] = True
            logger.debug("CLI override: quality_loop enabled")
        
        if hasattr(args, 'quality_iterations') and args.quality_iterations:
            self.config['quality_loop']['max_iterations'] = args.quality_iterations
            logger.debug(f"CLI override: quality_iterations = {args.quality_iterations}")
        
        if hasattr(args, 'validation_method') and args.validation_method:
            self.config['quality_loop']['validation_method'] = args.validation_method
            logger.debug(f"CLI override: validation_method = {args.validation_method}")
        
        # Metrics settings
        if hasattr(args, 'no_metrics') and args.no_metrics:
            self.config['metrics']['enabled'] = False
            logger.debug("CLI override: metrics disabled")
        
        if hasattr(args, 'show_metrics') and args.show_metrics:
            self.config['metrics']['show_summary'] = True
            logger.debug("CLI override: show_metrics enabled")
    
    def get(self, key_path: str, default=None):
        """
        Get config value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., 'quality_loop.enabled')
            default: Default value if key not found
            
        Returns:
            Config value or default
            
        Example:
            config.get('quality_loop.enabled')  # Returns True/False
            config.get('pipeline.count', 5)     # Returns count or 5
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def print_summary(self):
        """Print configuration summary."""
        logger.info("=" * 60)
        logger.info("📋 Configuration Summary")
        logger.info("=" * 60)
        
        # Pipeline
        logger.info("Pipeline:")
        logger.info(f"  Query: {self.get('pipeline.query', 'Not set')}")
        logger.info(f"  Count: {self.get('pipeline.count')}")
        logger.info(f"  Mode: {self.get('pipeline.mode')}")
        if self.get('pipeline.mode') == 'byod':
            logger.info(f"  Image Dir: {self.get('pipeline.image_dir')}")
        
        # Quality Loop
        logger.info("\nQuality Loop:")
        enabled = self.get('quality_loop.enabled')
        logger.info(f"  Enabled: {'✅ Yes' if enabled else '❌ No'}")
        if enabled:
            logger.info(f"  Max Iterations: {self.get('quality_loop.max_iterations')}")
            logger.info(f"  Validation Method: {self.get('quality_loop.validation_method')}")
        
        # Annotation
        logger.info("\nAnnotation:")
        logger.info(f"  Workers: {self.get('annotation.num_workers')}")
        
        # Metrics
        logger.info("\nMetrics:")
        logger.info(f"  Enabled: {'✅ Yes' if self.get('metrics.enabled') else '❌ No'}")
        logger.info(f"  Show Summary: {'✅ Yes' if self.get('metrics.show_summary') else '❌ No'}")
        
        logger.info("=" * 60)


# Global config instance
_config_instance: Optional[Config] = None


def initialize_config(config_path: Optional[str] = None, args=None) -> Config:
    """
    Initialize global configuration.
    
    Args:
        config_path: Path to YAML config file
        args: CLI arguments to override config
        
    Returns:
        Config instance
    """
    global _config_instance
    _config_instance = Config(config_path)
    
    if args:
        _config_instance.override_from_args(args)
    
    return _config_instance


def get_config() -> Config:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
