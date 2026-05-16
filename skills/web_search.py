from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 5):
    """Performs a web search using DuckDuckGo and returns summaries."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return "I couldn't find any relevant information on the web, sir."
        
        summary = "I've searched the web and found the following:\n"
        for i, res in enumerate(results, 1):
            summary += f"{i}. {res['title']}: {res['body']} (Source: {res['href']})\n"
            
        return summary
    except Exception as e:
        return f"I encountered an error while searching the web: {str(e)}"

if __name__ == "__main__":
    # print(web_search("current weather in London"))
    pass
