from datetime import datetime
from Utilities.utilities import log
import xml.etree.ElementTree as ET
import re
import requests
import json



def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text


def get_live_cricket_scores(team=None):
    # Map full names & abbreviations so filtering works either way
    team_aliases = {
        "india": ["india", "ind"],
        "australia": ["australia", "aus"],
        "england": ["england", "eng"],
        "new zealand": ["new zealand", "nz"],
        "south africa": ["south africa", "sa", "rsa"],
        "pakistan": ["pakistan", "pak"],
        "sri lanka": ["sri lanka", "sl"],
        "west indies": ["west indies", "wi"],
        "bangladesh": ["bangladesh", "ban"],
        "afghanistan": ["afghanistan", "afg"],
        "zimbabwe": ["zimbabwe", "zim"],
        "ireland": ["ireland", "ire"],
    }

    international_keywords = [
        "india", "australia", "england", "new zealand", "south africa",
        "pakistan", "sri lanka", "west indies", "bangladesh", "afghanistan",
        "zimbabwe", "ireland", "ind", "aus", "eng", "nz", "sa", "rsa",
        "pak", "sl", "wi", "ban", "afg", "ipl", "world cup", "t20i", "odi", "test"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    all_scores = []

    # 1. Try Cricbuzz Live Scores (captures International + League + Status clearly)
    try:
        cb_resp = requests.get("https://www.cricbuzz.com/cricket-match/live-scores", headers=headers, timeout=10)
        # Extract match titles and live score snippets from Cricbuzz HTML
        matches = re.findall(r'title="([^"]+ vs [^"]+, [^"]+)"', cb_resp.text)
        for m in dict.fromkeys(matches):
            all_scores.append(m)
    except Exception:
        pass

    # 2. Also fetch ESPNcricinfo RSS feed for live numeric scorelines
    try:
        rss_resp = requests.get("https://static.cricinfo.com/rss/livescores.xml", headers=headers, timeout=10)
        root = ET.fromstring(rss_resp.content)
        for item in root.findall(".//item"):
            title = item.find("title").text
            if title and title not in all_scores:
                all_scores.append(title)
    except Exception as e:
        if not all_scores:
            return f"Error fetching cricket scores: {e}"

    if not all_scores:
        return "No live cricket matches found right now."

    # Filter if user asked for a specific team
    if team:
        t_lower = team.lower().strip()
        search_terms = team_aliases.get(t_lower, [t_lower])
        filtered = [
            s for s in all_scores
            if any(re.search(rf"\b{re.escape(term)}\b", s.lower()) for term in search_terms)
        ]
        if not filtered:
            return f"No live match currently running for '{team}'. Active matches:\n" + "\n".join(all_scores[:8])
        return "\n".join(filtered[:10])

    # Sort so International matches appear BEFORE domestic matches
    def is_international(score_str):
        s_low = score_str.lower()
        return any(re.search(rf"\b{re.escape(kw)}\b", s_low) for kw in international_keywords)

    intl_matches = [s for s in all_scores if is_international(s)]
    domestic_matches = [s for s in all_scores if not is_international(s)]

    combined = []
    if intl_matches:
        combined.append("International / Major Matches:")
        combined.extend(intl_matches[:10])
    if domestic_matches:
        combined.append("\nDomestic Matches:")
        combined.extend(domestic_matches[:5])

    return "\n".join(combined)

#TOOLS = [{}, {}, {}]
TOOLS = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Returns the current date and time as a formatted string.",
            "parameters" : { "type" : "object", "properties" : {}},
        },
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_city_weather",
            "description" : "Returns the current weather for a given city.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "city" : {
                        "type" : "string",
                        "description" : "City to get the weather for.",
                    }
                },
                "required":["city"]
            },
        },
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_live_cricket_scores",
            "description" : "Returns live cricket match scores. Can optionally filter by a team or country name.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "team" : {
                        "type" : "string",
                        "description" : "Optional team name to filter live scores (e.g., 'India', 'Australia', 'CSK').",
                    }
                }
            },
        },
    }
]


FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_live_cricket_scores" : get_live_cricket_scores,
}


def run_tool(tool_call):
    func_name = tool_call.function.name
    try:
        func_args = json.loads(tool_call.function.arguments or "{}")
        log(f"{func_name} called with arguments: {func_args}")
        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        result = fn(**func_args)
    except Exception as e:
        result = f"Error calling function {func_name}: {str(e)}"
    
    log(f"{result}")
    return result