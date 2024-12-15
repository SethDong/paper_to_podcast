import requests
import json
from typing import List, Optional

class CustomChatModel:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str) -> str:
        """生成回复"""
        messages = [{"role": "user", "content": prompt}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": messages,
            "model": self.model
        }
        
        response = requests.post(
            "https://api.302.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        result = json.loads(response.text)["choices"][0]["message"]["content"]
        print(result)
        return result
    