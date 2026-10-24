from datetime import datetime
import xml.etree.ElementTree as ET
import requests


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    return response.text


def get_live_cricket_scores(team=None):
    url = "https://static.cricinfo.com/rss/livescores.xml"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        scores = [item.find("title").text for item in root.findall(".//item")]

        if team:
            scores = [s for s in scores if team.lower() in s.lower()]

        if not scores:
            return f"No live cricket matches found{f' for {team}' if team else ''}."

        return "\n".join(scores[:10])
    except Exception as e:
        return f"Error fetching cricket scores: {e}"


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
                },
            },
        },
    }
]


FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_live_cricket_scores" : get_live_cricket_scores,
}