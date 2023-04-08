from pydantic import BaseModel
from typing import List

class LLMInterface(BaseModel):
    model :str

    def generate(self, prompt: str, stop: List[str] = None):
        raise NotImplementedError("generate() method not implemented") # Implemented in subclass 