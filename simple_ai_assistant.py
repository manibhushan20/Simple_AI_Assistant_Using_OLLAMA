from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAPPING
import json
import os
import re


def clean_response(content):
    if not content:
        return ""
    return re.sub(
        r"<function-call>.*?</function-call>", "", content, flags=re.DOTALL
    ).strip()


def main():
    load_dotenv()

    client = OpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY")
    )

    messages = [{
        "role": "system",
        "content": (
            "Be a helpful, humble assistant. Answer directly in clear, natural "
            "language and keep responses under 120 words. Never show tool calls, "
            "function-call markup, internal reasoning, or tool-routing details."
        )
    }]

    while True:
        user_input = input("\nManibhushan: ")

        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("Exiting the assistant. Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )
        msg = response.choices[0].message

        while msg.tool_calls:
            messages.append(msg.model_dump(exclude_none=True))

            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments or "{}")
                function = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
                result = function(**func_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            response = client.chat.completions.create(
                model=os.getenv("MODEL"),
                messages=messages,
                tools=TOOLS
            )
            msg = response.choices[0].message

        content = clean_response(msg.content)
        if content:
            messages.append({"role": "assistant", "content": content})
            print("Assistant: " + content)


if __name__ == "__main__":
    main()
