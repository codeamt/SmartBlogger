import requests
import os
import re


def execute_perplexity_search(query: str, state=None) -> list:
    """Use Perplexity API for high-quality web search"""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return []

    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build model try-order: env first, then known-good fallbacks
        last_error = None
        env_model = os.getenv("PERPLEXITY_MODEL", "sonar")
        try_order = [env_model] if env_model else []
        # Append common online models (avoid duplicates / Nones)
        for m in ["sonar", "sonar-medium-online", "sonar-small-online"]:
            if m and m not in try_order:
                try_order.append(m)

        last_error = None
        for model_name in try_order:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Provide accurate, recent information with sources. Focus on technical and programming topics."
                    },
                    {
                        "role": "user",
                        "content": f"Search for: {query}. Provide 3-5 key findings with sources from the last 2 years. Include URLs."
                    }
                ],
                "max_tokens": 1000
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return parse_perplexity_response(content, query)
            else:
                text = response.text[:160].replace("\n", " ") if hasattr(response, 'text') else ""
                print(f"Perplexity API error for model '{model_name}': {response.status_code} {text}")
                last_error = (response.status_code, text)

        # If all models failed
        return []

    except Exception as e:
        print(f"Perplexity search error: {e}")
        return []


def parse_perplexity_response(content: str, query: str) -> list:
    """Parse Perplexity API response into structured results"""
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    results = []
    current = None

    bullet_re = re.compile(r"^(?:[•\-\*]|\d+\.)\s*(.+)$")

    for line in lines:
        m = bullet_re.match(line)
        if m:
            # Start a new item
            if current and current.get('content'):
                results.append(current)
            text = m.group(1).strip()
            current = {
                'content': text,
                'title': ' '.join(text.split()[:8]) or query
            }
            continue

        if line.startswith('http'):
            if not current:
                current = {'content': query, 'title': query}
            current['url'] = line
            if 'title' not in current or not current['title']:
                current['title'] = query

    if current and current.get('content'):
        results.append(current)

    # If nothing matched bullets, try to split paragraphs
    if not results:
        para = content.split('\n\n')
        for p in para:
            text = p.strip()
            if len(text) > 20:
                results.append({'content': text, 'title': ' '.join(text.split()[:8])})
                if len(results) >= 5:
                    break

    return results[:5]