"""
Conversation History Module

Stores and retrieves chat history for the RAG assistant.
"""

import json
import os
import re


class ConversationHistory:
    """
    Handles storage and retrieval of chat conversations.
    """

    def __init__(self, path="data/chat_history.json"):
        self.path = path

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def load_all(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def get_chat_ids(self):
        data = self.load_all()
        return list(data.keys())

    def load_history(self, chat_id):
        data = self.load_all()
        return data.get(chat_id, [])

    def save_interaction(self, chat_id, question, answer):
        data = self.load_all()

        if chat_id not in data:
            data[chat_id] = []

        data[chat_id].append({
            "question": question,
            "answer": answer
        })

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def create_new_chat(self):
        data = self.load_all()
        chat_numbers = []

        for chat_id in data.keys():
            match = re.fullmatch(r"chat_(\d+)", chat_id)
            if match:
                chat_numbers.append(int(match.group(1)))

        next_number = max(chat_numbers, default=0) + 1
        new_id = f"chat_{next_number}"

        while new_id in data:
            next_number += 1
            new_id = f"chat_{next_number}"

        data[new_id] = []

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

        return new_id
