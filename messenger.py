import requests

from config import PUSHOVER_TOKEN, PUSHOVER_URL, PUSHOVER_USER


def push(message: str) -> None:
    """Send a push notification to the phone via Pushover."""
    print(f"Push: {message}")
    requests.post(
        PUSHOVER_URL,
        data={"user": PUSHOVER_USER, "token": PUSHOVER_TOKEN, "message": message},
    )
