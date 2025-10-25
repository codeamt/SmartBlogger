#!/bin/bash
# Clear Python and Streamlit caches

echo "🧹 Clearing Python bytecode cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "🧹 Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null

echo "✅ Cache cleared! Now restart the app with:"
echo "   uv run streamlit run app.py"
