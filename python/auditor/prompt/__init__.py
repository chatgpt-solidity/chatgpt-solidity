

from abc import ABC, abstractmethod
from enum import Enum
import os
import shutil
from typing import Dict

from auditor.sol_file_folder import SolFileFolder
from python.auditor.fs import write_json_file




class PromptsGenerator(ABC):
    def __init__(
        self,
        cf: SolFileFolder,
        erc_rules: Dict,
    ) -> None:
        super().__init__()
        self.cf = cf
        self.erc_rules = erc_rules
        # mapping of children folder => hash
        self.llm_children_hashes = {}

    def backup_hashes(self):
        curr_hashes_path = self.get_hashes_path(self.cf.folder_path)
        if os.path.exists(self.get_hashes_path(self.cf.folder_path)):
            prev_hashes_path = self.get_prev_hashes_path(self.cf.folder_path)
            shutil.move(curr_hashes_path, prev_hashes_path)

    def get_hashes_path(self, folder: str):
        return os.path.join(folder, "llm_hashes.json")
    
    def get_conversation_dir(self, llm_folder, fname, category, idx, contract_name):
        return os.path.join(
            llm_folder,
            f"{contract_name}_{fname}_{category}_{idx}",
        )
    
    def dump_hashes(self, folder: str):
        path = self.get_hashes_path(folder)
        write_json_file(path, self.llm_children_hashes)

    def get_prev_hashes_path(self, folder: str):
        return os.path.join(folder, "llm_hashes.prev.json")

    @abstractmethod
    def generate(self):
        pass
