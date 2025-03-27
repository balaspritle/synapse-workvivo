from fastapi import FastAPI, Request, HTTPException
import requests, os

app = FastAPI()

WORKVIVO_API_URL = "https://api.workvivo.com/v1/chat/bots/message"
WORKVIVO_ID = os.getenv("WORKVIVO_ID")  # Set in env variables
WORKVIVO_TOKEN = os.getenv("WORKVIVO_TOKEN")  # Bearer token


def send_message(bot_userid: str, channel_url: str, message_type: str, payload: dict):
    """
    Sends a message to Workvivo via the bot API with authentication.
    """
    headers = {
        "Authorization": f"Bearer {WORKVIVO_TOKEN}",
        "Workvivo-Id": WORKVIVO_ID,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload.update({"bot_userid": bot_userid, "channel_url": channel_url, "type": message_type})

    response = requests.post(WORKVIVO_API_URL, headers=headers, json=payload)
    return response.json()


@app.get("/health")
def health_check():
    return {"status": "ok" + WORKVIVO_ID + WORKVIVO_TOKEN}


@app.post("/webhook")
async def webhook(request: Request):
    """
    Workvivo webhook that listens for messages and responds accordingly.
    """
    payload = await request.json()
    print("Incoming payload >>>", payload)
    sender_id = payload.get("sender", {}).get("id")
    text = payload.get("message", {}).get("text", "")
    channel_url = payload.get("channel", {}).get("url", "")

    if not sender_id or not text or not channel_url:
        raise HTTPException(status_code=400, detail="Invalid payload")

    bot_userid = "bot_user_id"  # Replace with your bot's user ID

    if text == "1":
        response = send_message(bot_userid, channel_url, "message", {"message": "Hello World"})

    elif text == "2":
        response = send_message(bot_userid, channel_url, "quick_reply", {
            "replies": [
                {"label": "Unable to connect to this network", "message": "Unable to connect to this network"},
                {"label": "Incorrect Password", "message": "Incorrect Password"},
                {"label": "No error message, just won’t connect", "message": "No error message, just won’t connect"},
                {"label": "Other", "message": "Other"}
            ]
        })

    elif text == "3":
        response = send_message(bot_userid, channel_url, "card", {
            "cards": [
                {
                    "cardTitle": "This is a title",
                    "cardDescription": "This is for secondary text",
                    "cardImage": "https://wordpress-zevigosolutions-assets.s3.ap-southeast-1.amazonaws.com/carrer.png",
                    "buttons": [
                        {"label": "IT Help", "message": "IT Help"},
                        {"label": "HR Help", "message": "HR Help"},
                        {"label": "Other", "message": "Other"}
                    ]
                }
            ]
        })

    else:
        response = send_message(bot_userid, channel_url, "message", {"message": f"Echo: {text}"})

    return response
