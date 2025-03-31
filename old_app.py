from flask import Flask, request, send_file, render_template, session, make_response
from flask_talisman import Talisman
import utility.utils as utils
# import utility.mail_service as mail_service
import utility.mail_service_v2 as mail_service
import utility.datastructures as datastructures
import utility.config as config_
import json
import concurrent.futures    
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
Talisman(app, force_https=False)

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
    response.headers['Cache-Control'] = "private, no-cache, no-store, must-revalidate"
    response.headers['Expires'] = -1
    response.headers['Pragma'] = "no-cache"
    response.headers['Content-Security-Policy'] = "default-src 'self'; font-src 'self'; img-src 'self'; script-src 'self'; style-src 'self'; frame-src 'self' titan.zevigosolutions.com"
    return response

@app.route("/")
def status():
    """This is the main function flask uses to listen at the `/` endpoint"""
    if request.method == 'GET':
        with open('docs/version_history.json', 'r') as f:
            data = json.load(f)            
        return "You are using version - {}".format(list(data.keys())[-1])
    
@app.route("/clear_cache")
def clear_cache():
    with open(config_.cache_path, "w") as outfile:
        outfile.write(json.dumps({}))
    return "Cache Cleared"

@app.route("/message" ,methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to listen at the `/message` endpoint"""
    if request.method == 'GET':
        return utils.verify_webhook(request)
    
    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        # print("payload", request, request.json)
        for x in event:
            if utils.is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                # print(">>", sender_id, text)
                utils.send_typing_action(sender_id)
                utils.respond(sender_id, text)
            if utils.is_postback_message(x):
                postback_payload = x['postback']['payload']
                sender_id = x['sender']['id']
                # print(">>", sender_id, postback_payload)
                utils.send_typing_action(sender_id)
                utils.respond(sender_id, postback_payload)
            if utils.is_quick_replies(x):
                text = x['message']['quick_reply']['payload']
                sender_id = x['sender']['id']
                # print(">>", sender_id, text)
                utils.send_typing_action(sender_id)
                utils.respond(sender_id, text)
        return "ok"
        
@app.route('/iris_analytics', methods=['GET','POST'])
def consolidated_mail_send():
    form = datastructures.InfoForm()
    if form.validate_on_submit():
        duration = None
        session['startdate'] = form.startdate.data
        session['enddate'] = form.enddate.data
        session['days'] = form.days.data
        
        if(session['days'] is not None):
            duration = int(session['days'])
        else:
            duration = tuple([session['startdate'], session['enddate']])
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = executor.map(mail_service.consolidated_analytics, [duration,])
            return render_template('date.html')
        except Exception as e:
            print("Error occured consolidated_mail_send", str(e))
    return render_template('index.html', form=form)

@app.route('/iris_analytics_trigger', methods=['GET'])
def consolidated_mail_send_trigger():
    try:
        mail_service.consolidated_analytics(7)
        return "OK"
    except Exception as e:
        print(e, "Error")
        return make_response("Bad Request", 400)
    
if __name__ == "__main__":
    docker_deploy = False
    if docker_deploy:
        app.run(port = 80, host = "0.0.0.0")
    else:
        app.run(port = 3000)