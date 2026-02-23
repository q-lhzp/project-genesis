import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_news(query: str):
    """
    Fetches latest headlines from Google News RSS for a specific query/location.
    """
    try:
        # Encode query for URL
        safe_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('utf-8')
            
        root = ET.fromstring(xml_data)
        headlines = []
        
        for item in root.findall('.//item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            headlines.append({
                "title": title,
                "url": link,
                "timestamp": pub_date,
                "category": "general"
            })
            
        return {"success": True, "headlines": headlines}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "World"
    result = fetch_news(query)
    print(json.dumps(result))
