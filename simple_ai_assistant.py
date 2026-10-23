from openai import OpenAI
from  dotenv import load_dotenv
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
  messages=messages
  )

  messages.append({"role": "assistant", "content": response.choices[0].message.content})

  print("Assistant: " + response.choices[0].message.content)




