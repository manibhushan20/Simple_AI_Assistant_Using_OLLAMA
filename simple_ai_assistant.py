from openai import OpenAI
from  dotenv import load_dotenv
import os

load_dotenv() #by default it will look for a .env file in the current directory


client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key=os.getenv("API_KEY")
)

while True:
  user_input = input("\nManibhushan:")

  if user_input.lower() in ["exit", "quit", "goodbye"]:
    print("Exiting the assistant. Goodbye!")
    break

  response =client.chat.completions.create(
  model=os.getenv("MODEL"),
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": user_input}
      ]
  )

  print("Assistant: " + response.choices[0].message.content)




