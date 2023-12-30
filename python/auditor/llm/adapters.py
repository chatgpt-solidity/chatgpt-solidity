from abc import ABC, abstractmethod
from typing import List
import openai


class LLMAdapter(ABC):
    @abstractmethod
    def ask(self, prompts) -> str:
        pass


class OpenAIGPT3(LLMAdapter):
    def ask(self, prompts) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", temperature=0, messages=prompts
        )
        choice = response["choices"][0]
        reply = choice["message"]["content"]
        return reply


class OpenAIGPT4(LLMAdapter):
    def ask(self, prompts) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-4", temperature=0, messages=prompts
        )
        choice = response["choices"][0]
        reply = choice["message"]["content"]
        return reply


class OpenAIGPT4Turbo(LLMAdapter):
    def ask(self, prompts) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview", temperature=0, messages=prompts
        )
        choice = response["choices"][0]
        reply = choice["message"]["content"]
        return reply


class LLAMA2P7B(LLMAdapter):
    """
    LLAMA2 7B parameters
    """

    def ask(self, prompts) -> str:
        pass
