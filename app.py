from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

# from fastapi import FastAPI, Request
from flask import Flask, request, send_file, render_template, session, make_response
from flask_talisman import Talisman
import json, secrets
import utility.utils as utils
import utility.mail_service_v2 as mail_service
import utility.config as config_

# app = FastAPI()
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
Talisman(app, force_https=False)


@app.route("/health" , methods=['GET'])
def health_check():
    with open('docs/version_history.json', 'r') as f:
            data = json.load(f)            
    return {"status": "You are using version - {}".format(list(data.keys())[-1])}


@app.route("/", methods=['GET', 'POST'])
def health():
    return {"status": "ok"}


@app.route("/clear_cache" ,methods=['GET'])
def clear_cache():
    with open(config_.cache_path, "w") as outfile:
        outfile.write(json.dumps({}))
    return {"status":  "Cache Cleared"}


@app.route("/webhook" ,methods=['POST'])
def webhook():
    """
    Workvivo webhook that listens for messages and responds accordingly.
    """
    if request.method == 'POST':
        payload = request.json

        print("Incoming payload >>>", payload)
        
        if "action" in payload.keys():
            bot_userid = payload.get("message", {}).get("bot_userid")
            text = payload.get("message", {}).get("message")
            channel_url = payload.get("message", {}).get("channel_url")
            user_email = payload.get("message", {}).get("user_email")
            print(">>> 1", bot_userid, text, channel_url, user_email)

            return utils.respond(bot_userid, channel_url, user_email, text)
        else:
            bot_userid = payload.get("bot", {}).get("bot_userid")
            text = payload.get("message", {}).get("text")
            channel_url = payload.get("channel", {}).get("channel_url")
            user_email = payload.get("sender", {}).get("user_id")
            print(">>> 2", bot_userid, text, channel_url, user_email)

            return utils.respond(bot_userid, channel_url, user_email, text)

# @app.route('/iris_analytics_trigger', methods=['GET'])
# def consolidated_mail_send_trigger():
#     if request.method == 'GET':
#         headers = request.headers
#         print("incoming headers at consolidated_mail_send_trigger", headers['Authorization'])

#         try:
#             mail_service.consolidated_analytics(7)
#             return "OK"
#         except Exception as e:
#             print(e, "Error")
#             return make_response("Bad Request", 400)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=8080)