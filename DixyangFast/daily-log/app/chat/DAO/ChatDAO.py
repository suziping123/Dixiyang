class ChatDAO:
    def __init__(self):
        self.chat_history = []

    def save_chat_record(self, question: str, answer: str):
        record = {
            "question": question,
            "answer": answer
        }
        self.chat_history.append(record)
        return record

    def get_chat_history(self, limit: int = 10):
        return self.chat_history[-limit:]

    def clear_history(self):
        self.chat_history = []