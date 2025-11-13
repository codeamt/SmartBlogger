# Image Processing Integration

This document explains how to use the image processing functionality in SmartBlogger, including both OCR and general image understanding capabilities.

## Overview

SmartBlogger now supports comprehensive image processing capabilities:

1. **Optical Character Recognition (OCR)**: Extract text from images using the DeepSeek-OCR model with vLLM acceleration.
2. **General Image Understanding**: Describe and analyze images using multimodal vision models.

This allows you to upload images and have both the text content extracted and the visual content described and analyzed.

## How It Works

1. When you upload an image file (PNG, JPEG, BMP, TIFF), the system automatically detects it as an image file.
2. The DeepSeek-OCR model processes the image and extracts text content using vLLM for acceleration.
3. The extracted text is then treated like any other text input and processed through the normal workflow.
4. The system generates summaries and uses the content for blog post generation.

## Requirements

To use the image processing functionality, you need to have the following dependencies installed:

- vllm
- transformers
- torch
- einops
- addict
- easydict
- flash-attn
- Pillow

Install these dependencies using:

```bash
pip install vllm transformers torch einops addict easydict flash-attn Pillow
```

## Usage

1. Start the SmartBlogger application
2. In the Content Input section, use the file uploader to upload image files
3. The system will automatically process the images and extract text
4. Continue with your normal workflow to generate blog posts

## Configuration

The image processor uses the following default settings:

- OCR Model: deepseek-ai/DeepSeek-OCR
- Vision Model: llava-hf/llava-1.5-7b-hf (example)
- Processing mode: Markdown (preserves document structure)
- vLLM acceleration with 50% GPU memory utilization for OCR
- vLLM acceleration with 30% GPU memory utilization for vision model
- Max model length: 4096 tokens for OCR, 2048 for vision

## Troubleshooting

If image processing is not working:

1. Check that all required dependencies are installed
2. Verify that the models can be downloaded (requires internet connection)
3. Check the application logs for error messages
4. Ensure sufficient system resources (the models require significant memory)

## Performance Benefits of vLLM

Using vLLM for image processing provides several performance benefits:

- Faster inference times
- Better memory management
- Support for continuous batching
- Optimized CUDA kernels
- Reduced latency for image processing

## Platform-Specific Optimizations

### Apple Silicon (M1/M2/M3) Support

The image processor includes optimizations for Apple Silicon Macs:

- Automatic detection of Apple Silicon hardware
- GPU-based processing when good GPU RAM is available
- Conservative GPU memory utilization (50-60%)
- Full model sequence lengths for better quality
- Support for MLX acceleration (when available)
- CPU fallback when necessary

On Apple Silicon with good GPU RAM (like your M2), the system will automatically:
- Use GPU processing for better performance
- Maintain full model capabilities
- Utilize MLX acceleration when available

### NVIDIA GPU Systems

For NVIDIA GPU systems:

- The image processor is configured to use only 50% of GPU memory for OCR and 30% for vision to avoid conflicts with Ollama
- Ollama is given priority for GPU resources as it's the primary LLM engine
- Full model capabilities are available

### Troubleshooting Memory Issues

If you experience memory issues on any platform, consider:
- Running image processing on CPU by setting `gpu_memory_utilization=0.0`
- Processing images sequentially rather than concurrently
- Reducing the `max_model_len` parameter further
- Using smaller images when possible

## Limitations

- Image processing may take some time depending on image size and system resources
- Accuracy may vary based on image quality and text complexity
- The models require significant system resources (GPU recommended)
