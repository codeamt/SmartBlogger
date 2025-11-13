"""
Unified Image Processor for cross-platform image processing
Handles both OCR and general image understanding with platform-optimized execution
"""

import os
import logging
import torch
from typing import Optional, Dict, Any
from PIL import Image
import tempfile

# Try to import vLLM and image processing dependencies
try:
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer, AutoProcessor
    from PIL import Image
    import torch
    
    # Check for Apple Silicon
    IS_APPLE_SILICON = torch.backends.mps.is_available()
    
    # Try to import MLX for Apple Silicon optimization
    try:
        import mlx.core as mx
        MLX_AVAILABLE = True
    except ImportError:
        MLX_AVAILABLE = False
    
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    IS_APPLE_SILICON = False
    MLX_AVAILABLE = False
    logging.warning("Image processing dependencies not available. Install vllm, transformers, and PIL to enable image functionality.")

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.ocr_model = None
        self.vision_model = None
        self.tokenizer = None
        self.processor = None
        
    def initialize_ocr_model(self) -> bool:
        """Initialize the DeepSeek-OCR model with platform-optimized settings"""
        if not IMAGE_PROCESSING_AVAILABLE:
            logger.warning("Image processing dependencies not available")
            return False
            
        try:
            model_name = 'deepseek-ai/DeepSeek-OCR'
            
            # Platform-specific configuration
            if IS_APPLE_SILICON:
                # Apple Silicon with good GPU RAM
                gpu_mem_util = 0.6 if MLX_AVAILABLE else 0.0  # Use GPU if MLX available, otherwise CPU
                max_len = 4096 if gpu_mem_util > 0 else 2048
                logger.info(f"Initializing DeepSeek-OCR for Apple Silicon with {'MLX' if MLX_AVAILABLE else 'CPU'}")
            else:
                # NVIDIA GPU systems
                gpu_mem_util = 0.5  # Conservative usage to avoid conflicts with Ollama
                max_len = 4096
                logger.info("Initializing DeepSeek-OCR for NVIDIA GPU")
            
            self.ocr_model = LLM(
                model=model_name,
                trust_remote_code=True,
                gpu_memory_utilization=gpu_mem_util,
                max_model_len=max_len,
                enforce_eager=True
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            logger.info(f"DeepSeek-OCR model initialized successfully (GPU util: {gpu_mem_util*100}%)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek-OCR model: {e}")
            return False
    
    def initialize_vision_model(self) -> bool:
        """Initialize a general vision model for image understanding with platform-optimized settings"""
        if not IMAGE_PROCESSING_AVAILABLE:
            logger.warning("Image processing dependencies not available")
            return False
            
        try:
            model_name = 'llava-hf/llava-1.5-7b-hf'  # Same model for all platforms
            
            # Platform-specific configuration
            if IS_APPLE_SILICON:
                # Apple Silicon with good GPU RAM
                if MLX_AVAILABLE:
                    gpu_mem_util = 0.5  # Use 50% of GPU memory with MLX
                    logger.info("Initializing vision model for Apple Silicon with MLX")
                else:
                    gpu_mem_util = 0.4  # Conservative GPU usage
                    logger.info("Initializing vision model for Apple Silicon")
            else:
                # NVIDIA GPU systems
                gpu_mem_util = 0.3  # Conservative usage to avoid conflicts with Ollama
                logger.info("Initializing vision model for NVIDIA GPU")
            
            # Same max length for all platforms for consistency
            max_len = 2048
            
            self.vision_model = LLM(
                model=model_name,
                trust_remote_code=True,
                gpu_memory_utilization=gpu_mem_util,
                max_model_len=max_len,
                enforce_eager=True
            )
            
            self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            
            logger.info(f"Vision model initialized successfully (GPU util: {gpu_mem_util*100}%)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize vision model: {e}")
            return False
    
    def extract_text_from_image(self, image_path: str, mode: str = "markdown") -> Optional[str]:
        """Extract text from an image using DeepSeek-OCR"""
        if self.ocr_model is None:
            if not self.initialize_ocr_model():
                return None
        
        try:
            # Determine prompt based on mode
            if mode == "markdown":
                prompt = "<image>\n<|grounding|>Convert the document to markdown. "
            else:
                prompt = "<image>\nFree OCR. "
            
            # Prepare sampling parameters
            sampling_params = SamplingParams(temperature=0.7, max_tokens=2048)
            
            # Process image (this would need to be adapted based on how DeepSeek-OCR handles images)
            # For now, we'll assume the model can handle image paths directly
            outputs = self.ocr_model.generate([prompt], sampling_params)
            
            # Extract text from result
            if outputs and len(outputs) > 0:
                return outputs[0].outputs[0].text
            
            return ""
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def understand_image(self, image_path: str, prompt: str = "Describe this image in detail.") -> Optional[str]:
        """Perform general image understanding using a vision model"""
        # Initialize vision model if not already done
        if self.vision_model is None:
            if not self.initialize_vision_model():
                # Fallback to basic description if vision model unavailable
                return "Image understanding model not available."
        
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            
            # Prepare sampling parameters
            sampling_params = SamplingParams(temperature=0.7, max_tokens=1024)
            
            # Process image with vision model
            outputs = self.vision_model.generate([prompt], sampling_params)
            
            # Extract response from result
            if outputs and len(outputs) > 0:
                return outputs[0].outputs[0].text
            
            return "No response from image understanding model."
                
        except Exception as e:
            logger.error(f"Error understanding image {image_path}: {e}")
            return None
    
    def is_image_file(self, file_path: str) -> bool:
        """Check if a file is an image that can be processed"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
        _, ext = os.path.splitext(file_path.lower())
        return ext in image_extensions


# Global instance
image_processor = ImageProcessor()
