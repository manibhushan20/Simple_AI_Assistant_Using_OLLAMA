from openai import OpenAI
from  dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAPPING
import json
import os

load_dotenv() #by default it will look for a .env file in the current directory


client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key=os.getenv("API_KEY")
)

messages = []

messages.append({"role":"system","content":"Act like a humble agent and always respond under 120 words." })

while True:
  user_input = input("\nManibhushan:")

  if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
    print("Exiting the assistant. Goodbye!")
    break

  messages.append({"role": "user", "content": user_input})

  response =client.chat.completions.create(
  model=os.getenv("MODEL"),
  messages=messages,
  tools=TOOLS
  )

  msg = response.choices[0].message
  if msg.tool_calls:
    messages.append(msg)

    for tool_call in msg.tool_calls:
      func_name = tool_call.function.name
      func_args = json.loads(tool_call.function.arguments or "{}")

      fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
      result = fn(**func_args)

      messages.append({
        "role":"tool",
        "tool_id":tool_call.id,
        "content":str(result)
      })

      #2nd call to LLm
      response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
      )

      msg = response.choices[0].message

      messages.append({
        "role":"assistant",
        "content":msg.content
      })

      print("Assistant: " + msg.content)


  messages.append({"role": "assistant", "content": response.choices[0].message.content})

  print("Assistant: " + response.choices[0].message.content)




