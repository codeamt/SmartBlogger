# SmartBlogger

SmartBlogger is an AI-powered blogging assistant that helps you create high-quality, original content with integrated research capabilities and plagiarism detection.

## Features

- **AI-Powered Content Generation**: Create blog posts from code, documents, or ideas
- **Multi-Source Research**: Research from Arxiv, Web, GitHub, and Substack
- **Plagiarism Detection**: Built-in originality checking
- **Local LLM Support**: Works with Ollama for fully local AI processing
- **Image Processing**: Extract text from images using DeepSeek-OCR with vLLM acceleration and perform general image understanding
- **Customizable Writing Style**: Adjust tone, audience, and content preferences

## Getting Started

1. Install dependencies using uv (recommended):
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   pip install -e .
   ```

2. Install Ollama from https://ollama.ai

3. Start the application:
   ```bash
   streamlit run app.py
   ```
   
   Or using the project script:
   ```bash
   uv run streamlit run app.py
   ```

## Image Processing

SmartBlogger now supports comprehensive image processing capabilities:

1. **Optical Character Recognition (OCR)**: Extract text from images using the DeepSeek-OCR model with vLLM acceleration. This allows you to upload images containing text (such as screenshots of documents, handwritten notes, charts, etc.) and have the text automatically extracted and processed.

2. **General Image Understanding**: Describe and analyze images using multimodal vision models.

Supported image formats: PNG, JPEG, BMP, TIFF

For more details on image processing capabilities, see [Image Processing Guide](docs/IMAGE_PROCESSING.md).

For Apple Silicon users, see [Apple Silicon Optimization Guide](docs/APPLE_SILICON.md).

For development setup and contribution guidelines, see [Development Guide](docs/DEVELOPMENT.md).

## Requirements

- Python 3.11+
- Ollama (for local LLM support)
- Internet connection (for research and initial model download)

## Development Tools (Optional but Recommended)

- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package installer and resolver

## Platform Support

- **NVIDIA GPUs**: Full support with vLLM acceleration
- **Apple Silicon (M1/M2/M3)**: Optimized processing with MLX acceleration (included by default)
- **Intel CPUs**: Standard CPU processing

## Configuration

Set environment variables in a `.env` file:

```
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_WRITER_MODEL=llama3.1:8b
LOCAL_RESEARCHER_MODEL=llama3.1:8b
TAVILY_API_KEY=your_tavily_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
```

## License

MIT
