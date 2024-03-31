from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid

app = FastAPI()

# Directory to store conversation logs
LOGS_DIR = "conversation_logs"


class Conversation(BaseModel):
    message: str
    model: str


def create_logs_dir():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)


def save_conversation_log(conversation_id, model, conversation_logs):
    log_file_path = os.path.join(LOGS_DIR, f"{model}-{conversation_id}.txt")
    with open(log_file_path, "a") as file:
        for log_entry in conversation_logs:
            file.write(log_entry + "\n")


@app.post('/start_conversation', response_model=dict)
def start_conversation(conversation: Conversation):
    message = conversation.message
    model = conversation.model

    conversation_id = str(uuid.uuid4())
    conversation_logs = [f"CONVERSATION:\n{message}"]

    create_logs_dir()
    save_conversation_log(conversation_id, model, conversation_logs)

    return {'conversation_id': conversation_id}

@app.post('/continue_conversation/{conversation_id}', response_model=dict)
def continue_conversation(conversation_id: str, conversation: Conversation):
    message = conversation.message
    model = conversation.model

    if not os.path.exists(os.path.join(LOGS_DIR, f"{model}-{conversation_id}.txt")):
        raise Exception(status_code=404, detail="Conversation ID not found")

    save_conversation_log(conversation_id, model, [message])

    return {'status': 'Message added to the conversation'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8111)