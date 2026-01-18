import csv
import os
from datetime import datetime

LOG_FILE = "tokens_log.csv"

def log_tokens(model, usage, tag="correccion"):
    if not usage:
        return

    exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow([
                "timestamp",
                "model",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "tag"
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            tag
        ])
print("LOG ESCRITO")
