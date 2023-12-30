from abc import ABC, abstractmethod
import os
import shutil

from auditor.llm.adapters import LLMAdapter


class PlugIn(ABC):
    def __init__(
        self, name: str, auditor: LLMAdapter, conversation_folder: str
    ) -> None:
        self.conversation_folder = conversation_folder
        self.name = name
        self.auditor = auditor

    def get_plugin_conversation_folder(self):
        return os.path.join(self.conversation_folder, "plugins", self.name)

    def create_plugin_conversation_folder(self):
        os.makedirs(self.get_plugin_conversation_folder(), exist_ok=True)

    def clean_plugin_conversation_folder(self):
        folder = self.get_plugin_conversation_folder()
        if os.path.exists(folder):
            shutil.rmtree(folder)

    @abstractmethod
    def run(self, force=False):
        pass
