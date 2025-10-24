import requests
import os


def execute_perplexity_search(query: str) -> list:
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

        payload = {
            "model": "sonar-medium-online",
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
            content = data['choices'][0]['message']['content']
            return parse_perplexity_response(content, query)
        else:
            print(f"Perplexity API error: {response.status_code}")
            return []

    except Exception as e:
        print(f"Perplexity search error: {e}")
        return []


def parse_perplexity_response(content: str, query: str) -> list:
    """Parse Perplexity API response into structured results"""
    # This is a simplified parser - you might want to make it more robust
    lines = content.split('\n')
    results = []
    current_result = {}

    for line in lines:
        line = line.strip()
        if line.startswith('•') or line.startswith('-'):
            if current_result and 'content' in current_result:
                results.append(current_result)
                current_result = {}

            current_result['content'] = line[1:].strip()
        elif line.startswith('http'):
            current_result['url'] = line
            current_result['title'] = query  # Use query as fallback title

    # Add the last result
    if current_result and 'content' in current_result:
        results.append(current_result)

    return results[:5]  # Limit to top 5 results