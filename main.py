from fastapi import FastAPI, Request
import requests, os, json

app = FastAPI()

WORKVIVO_API_URL = os.getenv("WORKVIVO_API_URL")
WORKVIVO_ID = os.getenv("WORKVIVO_ID")  # Set in env variables
WORKVIVO_TOKEN = os.getenv("WORKVIVO_TOKEN")  # Bearer token


def send_message(bot_userid: str, channel_url: str, message_type: str, payload: dict):
    """
    Sends a message to Workvivo via the bot API with authentication.
    """
    headersList = {
        "Accept": "*/*", 
        "Accept": "application/json",
        "Workvivo-Id": WORKVIVO_ID,
        "Authorization": f"Bearer {WORKVIVO_TOKEN}",
        "Content-Type": "application/json" 
    }
    
    payload.update({"bot_userid": bot_userid, "channel_url": channel_url, "type": message_type})
    
    response = requests.request("POST", WORKVIVO_API_URL, data=json.dumps(payload), headers=headersList)
    print("response", response, response.json())
    print("headersList", headersList)
    print("payload", payload)

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

    bot_userid = payload.get("message", {}).get("bot_userid")
    text = payload.get("message", {}).get("message", "")
    channel_url = payload.get("message", {}).get("channel_url", "")
    print(bot_userid, text, channel_url)

    if text == "1":
        response = send_message(bot_userid, channel_url, "message", {"message": "Hello World"})

    elif text == "2":
        response = send_message(bot_userid, channel_url, "quick_reply", {
            "replies": [
                {"label": "Unable to connect to this network", "message": "Unable to connect to this network"},
                {"label": "Incorrect Password", "message": "Incorrect Password"},
                {"label": "No error message, just won't connect", "message": "No error message, just won't connect"},
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