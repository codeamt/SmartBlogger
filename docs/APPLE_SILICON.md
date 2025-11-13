# Apple Silicon Optimization Guide

This guide explains how to optimize SmartBlogger for Apple Silicon Macs (M1, M2, M3 chips).

## Overview

SmartBlogger includes automatic optimizations for Apple Silicon Macs that provide better performance and compatibility compared to standard CPU processing.

## Automatic Optimizations

When running on Apple Silicon, SmartBlogger automatically:

1. **Detects Apple Silicon hardware** using PyTorch MPS backend
2. **Uses GPU processing** when good GPU RAM is available (like your M2)
3. **Conservatively utilizes GPU memory** (50-60% usage) to avoid conflicts
4. **Maintains full model sequence lengths** for better quality
5. **Enables MLX acceleration** when available
6. **Falls back to CPU** only when necessary

## MLX Support

MLX dependencies are now included by default in the main installation, so no additional installation steps are required for Apple Silicon optimization.

For development or testing of alternative MLX configurations, you can still use the optional dependency:

```bash
pip install -e .[apple-silicon]
```

## Performance Considerations

### Model Size Recommendations

For Apple Silicon, we recommend using smaller models:

- **OCR**: DeepSeek-OCR (automatically optimized)
- **Vision**: Smaller LLaVA variants or specialized edge models

### Memory Management

Apple Silicon optimizations include:

- Automatic CPU fallback for large models
- Reduced batch sizes
- Memory-efficient processing
- Background processing to avoid UI freezes

## Troubleshooting

### Common Issues

1. **Slow Processing**: This is expected for large models on CPU. Consider using smaller models.
2. **Memory Errors**: Reduce image sizes or use the CPU-only mode.
3. **Model Loading Failures**: Ensure sufficient system memory (16GB+ recommended).

### Solutions

1. **For Slow Processing**:
   - Use smaller images
   - Process one image at a time
   - Consider using cloud-based processing for large batches

2. **For Memory Errors**:
   - Reduce `max_model_len` in the processor configuration
   - Close other memory-intensive applications
   - Use the `gpu_memory_utilization=0.0` setting

3. **For Model Loading Failures**:
   - Ensure 16GB+ RAM
   - Use smaller models
   - Increase virtual memory if needed

## Performance Tips

1. **Image Preprocessing**:
   - Resize large images before processing
   - Use compressed image formats
   - Process images in batches of 1-2

2. **System Configuration**:
   - Close unnecessary applications
   - Ensure adequate cooling
   - Monitor Activity Monitor for resource usage

3. **Model Selection**:
   - Use quantized models when available
   - Consider distilled versions of large models
   - Test different models for your specific use case

## Future Improvements

We're continuously working on improving Apple Silicon support:

- Native MLX implementations
- Better model quantization
- Improved memory management
- Enhanced performance optimizations

## Feedback

If you encounter any issues or have suggestions for Apple Silicon optimizations, please open an issue on our GitHub repository.
