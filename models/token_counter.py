# models/token_counter.py
import tiktoken

def count_tokens(messages, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        total += len(enc.encode(content))
    return total
