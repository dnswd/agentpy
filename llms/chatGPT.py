import openai

from llms.base import LLMInterface
from os import environ as env
from typing import List

class ChatGPT(LLMInterface):
    """Use ChatGPT as LLM Model"""

    model: str = "gpt-3.5-turbo"
    temperature: float = 0.0
    openai.api_key = env.get("OPENAI_API_KEY", None)

    def generate(self, prompt: str, stop: List[str] = None):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            stop=stop
        )
        return response.choices[0].message.content

if __name__ == '__main__':
    llm = ChatGPT()
    result = llm.generate(prompt='Who is the president of the USA?')
    print(result)
