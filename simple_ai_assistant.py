#standard library imports
import os

#Third party imports
from openai import OpenAI
from dotenv import load_dotenv

#Local module imports
from tools import TOOLS, run_tool
from Utilities.utilities import log


load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []

MAX_STEPS = 5

messages.append(
    {
        "role" : "system",
        "content": "Act like a very humble agent and respond always under 200 words."
    }
)



while True:
    user_input = input("\nManibhushan: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )



#Chained tool calling
    for step in range(MAX_STEPS):

        response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,
       )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        log(f"Step {step + 1}: model requested {len(msg.tool_calls)} tool calls.")

        messages.append(msg)

        for tool_call in msg.tool_calls:
            result = run_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id" : tool_call.id,
                "content" : str(result),
            })


    else:
        fallback ="Sorry, I could not finish this within the maximum number of steps."
        messages.append({
            "role" : "assistant",
            "content" : fallback
        })
        print("Assistant: " + fallback)
        continue

    messages.append({
        "role" : "assistant",
        "content" : msg.content
    })

    print("Assistant: " + msg.content or "")