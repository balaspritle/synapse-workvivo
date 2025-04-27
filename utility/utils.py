import utility.config as config, utility.azure_bot as azure_bot, utility.db_utils as db_utils, utility.workvivo as workvivo_utils, utility.mail_service_v2 as mail_service
from utility.attachments import attachment_mapper_swapped
from utility.datastructures import WORKVIVO_FORMATTER, DATA_COLLECTOR
import requests, random, datetime, pytz, time, os, json, ast, re
import numpy as np
import concurrent.futures    
from collections import namedtuple

WORKVIVO_API_URL = os.getenv("WORKVIVO_API_URL")
WORKVIVO_ID = os.getenv("WORKVIVO_ID")
WORKVIVO_TOKEN = os.getenv("WORKVIVO_TOKEN")
ECHO_BOT = ast.literal_eval(os.getenv("ECHO_BOT"))
GAME_MODE = ast.literal_eval(os.getenv("GAME_MODE"))

## GAMEPLAY
if GAME_MODE:
    print("GAME MODE IS ON")
    import utility.gameplay as gameplay
    gameplay_users_holder = {}

wf_format = WORKVIVO_FORMATTER()

users_chat_data_holder = {}
users_not_satisfied = {}
no_bot_match = {}
users_comments_collector = {}
returning_user_data_holder = []
email_trace = '$$$SYNAPSEEMAILHANDLER$$$'
new_hire_trace = {"ZEVIGOSOLUTIONSNHIRENO" : "No worries. How about medical claim process?", "ZEVIGOSOLUTIONSNHIRENO2" : "Sure. Give me a question or topic to start"}
special_messages = config.default_fallback_question + ['< No >', 'No', 'no', 'NO'] # Also include the default fallback question for email flow consideration.
holder = namedtuple('holder', 'messages prompts images files did_i_answer_your_question_flag')
headersList = {"Accept": "*/*",  "Accept": "application/json", "Workvivo-Id": WORKVIVO_ID, "Authorization": f"Bearer {WORKVIVO_TOKEN}","Content-Type": "application/json"}

def handling_emails(bot_userid, channel_url, sender, message):
    if(email_trace in message):
        send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_mail_sent_message)))
        send_message_v2(bot_userid, channel_url, sender, wf_format.prompt_messages_format(random.choice(config.default_did_I_answer_your_question), ['< Yes >', '< No >']))
        
        ## Send An Email Here based on the attachment_id ##
        # mail_data = [{'sender_id': sender, 'attachment_id': message.split(email_trace)[-1]}] ## ASync Email Push
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     futures = executor.map(push_mail_with_attachment, mail_data)
        # push_mail_with_attachment(mail_data[0])

        mail_data = {'sender_id': sender, 'attachment_id': message.split(email_trace)[-1]}
        response = requests.request("POST", "https://reychghlum7gcuaglw57ammvb40bulpu.lambda-url.ap-southeast-1.on.aws/", headers={'Content-Type': 'application/json'}, data=json.dumps(mail_data))
        return True ## Message handled here 
    return False ## Message not handled here
    
def handling_new_hires(bot_userid, channel_url, sender, message):
    if(list(new_hire_trace.keys())[0] == message):
        buttons, buttons_holder = [], []
        buttons.append({"type":"postback","title":"yes","payload":"How do I claim for my medical/dental expenses?"})
        buttons.append({"type":"postback","title":"no","payload":"ZEVIGOSOLUTIONSNHIRENO2"})
        buttons_holder.append({"title": list(new_hire_trace.values())[0], "buttons":buttons})
        send_message_v2(bot_userid, channel_url, sender, {"attachment":{"type":"template","payload":{"template_type":"generic", "elements": buttons_holder}}})  
        return True ## Message handled here 
    elif(list(new_hire_trace.keys())[1] == message):
        send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(list(new_hire_trace.values())[1])) 
        return True ## Message handled here 
    return False ## Message not handled here

def handling_numbers(bot_userid, channel_url, sender, message):
    try:
        if isinstance(int(message), int):
            hr_email_flag_3 = find_three_consecutive_not_found(users_chat_data_holder[sender].__dict__['chat_log'])
            if hr_email_flag_3:
                send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_no_flow_message)))
                send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_mail_flow_final_message)))
                user_data = [users_chat_data_holder[sender].__dict__] ## ASync Email Push
                with concurrent.futures.ThreadPoolExecutor() as executor: 
                    futures = executor.map(push_mail, user_data)
                del users_chat_data_holder[sender] ## Remove the user from the loop and start collecting fresh logs ##
                return True
            else:
                send_message_v2(sender, wf_format.message_format(random.choice(config.default_fallback_answer)))
                return True
    except ValueError as e:
        return False ## Message not handled here

def handling_user_comments(bot_userid, channel_url, sender, message):
    if sender in list(users_comments_collector.keys()):
        user_feedback_rating = users_chat_data_holder[sender].__dict__['chat_log'][-3]
        users_comments_collector[sender] = message ## User comments collection happens here
        if config.debug:
            print("user comment >>>>>>>>", users_comments_collector[sender], user_feedback_rating)
        # push_mail(sender, "USER COMMENT AND RATING", " User Comment :" + users_comments_collector[sender] + ", Feedback Rating :" +str(user_feedback_rating))
        collect_comments_and_rating(sender, users_comments_collector[sender], user_feedback_rating)
        send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_comments_response_message)))
        
        ## PUSH AN EMAIL HERE WITH THE COMMENT DATA ##
        del users_comments_collector[sender] ## Remove the user from the loop ##
        del users_chat_data_holder[sender] ## Remove the user from the loop and start collecting fresh logs ##
        return True ## Message handled here
    return False ## Message not handled here

def game_redirection(bot_userid, channel_url, sender, message):
    response = False
    
    try:
        if sender in list(gameplay_users_holder.keys()):
            pass
        else:
            gameplay_users_holder[sender] = gameplay.gamezone() ## Register user for the first time in the gameplay ##
        
        print(">>>>>", gameplay_users_holder[sender].user_gameplay_stats)
        if message in gameplay_users_holder[sender].gameplay_secret_keyword + gameplay_users_holder[sender].gameplay_trigger_keyword:
            response = gameplay_users_holder[sender].gameResponseMain(bot_userid, channel_url, sender, message)
            
        elif message.startswith(gameplay_users_holder[sender].gamplay_correct_answer_prompt) or message.startswith(gameplay_users_holder[sender].gamplay_wrong_answer_prompt):
            response = gameplay_users_holder[sender].gameResponseMain(bot_userid, channel_url, sender, message)

        elif gameplay_users_holder[sender].user_gameplay_stats != {}:
            send_message_v2(bot_userid, channel_url, wf_format.message_format(random.choice(["Oh that's incorrect. Your game score will be submitted for the contest."])))
            send_message_v2(bot_userid, channel_url, wf_format.message_format("Would you like to play again ?"))
            gameplay_users_holder[sender].over_and_out(sender)
            gameplay_users_holder[sender].game_initialization(sender, "sample message", override = True)
            response = True

        ## Check user's status
        if not gameplay_users_holder[sender].user_status:
            del gameplay_users_holder[sender]
        
        return response        
    except Exception as e:
        print("Error in >>>>>>>> game_redirection", e)

def redirection(bot_userid, channel_url, sender, message):
    if config.debug:
        print("sender : {}, message ---> {} \n".format(sender, message))
    
    if handling_emails(bot_userid, channel_url, sender, message):
        return True ## Message handled here            
    
    if handling_user_comments(bot_userid, channel_url, sender, message):
        return True ## Message handled here
    
    # if handling_new_hires(bot_userid, channel_url, sender, message):
    #     return {"status": "ok"} ## Message handled here
    
    if handling_numbers(bot_userid, channel_url, sender, message):
        return True ## Message handled here
    
    if message in special_messages:
        if message in special_messages[-3:]: ## If the user is manually typing No, no, then handle here ##
            send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_fallback_answer)))
            return True ## Message handled here
        try:
            users_not_satisfied[sender] += 1
        except KeyError:
            users_not_satisfied[sender] = 1
            
        ## Also record the user not satisfied data in the excel sheet ##
        timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d"))                
        query = "INSERT INTO user_not_satisfied (date, user_id, message_content) VALUES (%s, %s, %s)"
        argument = (timestamp, sender, str(message))
        db_utils.insert_data_to_db(query, argument)

        count = users_not_satisfied[sender]
        if count >= config.threshold:
            ## PUSH AN EMAIL HERE WITH THE CHAT DATA ##
            if config.debug:
                print("user data >>>>>>>>", users_chat_data_holder[sender].__dict__)
                
            # print(users_chat_data_holder[sender].__dict__[users_chat_data_holder[sender].__dict__.index("user : no"):])
            
            ## Check whether the user has said no consecutively for three times; otherwise ignore it ##
            hr_email_flag_1 = find_three_consecutive_no(users_chat_data_holder[sender].__dict__['chat_log'])
            
            if hr_email_flag_1:
                send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_no_flow_message)))
                send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_mail_flow_final_message)))
                user_data = [users_chat_data_holder[sender].__dict__] ## ASync Email Push
                with concurrent.futures.ThreadPoolExecutor() as executor: 
                    futures = executor.map(push_mail, user_data)
                
                # push_mail(users_chat_data_holder[sender].__dict__) ## Sync Email Push
                
                del users_not_satisfied[sender] ## Remove the user from the loop ##
                del users_chat_data_holder[sender] ## Remove the user from the loop and start collecting fresh logs ##
            else:
                # Track for the user comments again ##
                users_not_satisfied[sender] -= 1
                send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_fallback_answer)))
                
            return True ## Message handled here
        else:
            send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_fallback_answer)))
            return True
    
    return False
    
def respond(bot_userid, channel_url, sender, message):   
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    if GAME_MODE:
        game_redirection_flag = game_redirection(bot_userid, channel_url, sender, message)
        if game_redirection_flag:
            return {"status": "ok"}
    if ECHO_BOT:
        response = send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(f"Echo : {message}"))
        return response
        
    if sender in list(users_chat_data_holder.keys()):
        pass ## If the user is already there, then we can just continue ##
    else:
        users_chat_data_holder[sender] = DATA_COLLECTOR(sender_id = sender, chat_log = [], timestamps = []) ## Register user for the first time ##
    
    user_chat_timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d %H:%M:%S"))
    users_chat_data_holder[sender].store_logs(sender, user_chat_timestamp + " - User : " + message) ## Log user's message ##
    
    redirect_flag = redirection(bot_userid, channel_url, sender, message) ## Redirection happens here ##

    if redirect_flag:
        return {"status": "ok"}
    else:
        # response = azure_bot.azure_bot_response(message, sender)
        response = azure_bot.azure_bot_response_cqa(message, sender)
        formatted_response = postprocess_azure_response_v2(bot_userid, channel_url, sender, response, returning_user_data_holder)
        messages, prompts, images, files, did_i_answer_your_question_flag = formatted_response.messages, formatted_response.prompts, formatted_response.images,  formatted_response.files,  formatted_response.did_i_answer_your_question_flag
        if config.debug:
            print("messages, prompts, images, did_i_answer_your_question_flag", messages, prompts, images, did_i_answer_your_question_flag, "\n")
        if messages:
            response = send_message_v2(bot_userid, channel_url, sender, messages)
            if not images and not files and did_i_answer_your_question_flag:
                did_i_answer_your_question(bot_userid, channel_url, sender)
        if prompts:
            if(isinstance(prompts, tuple)):
                response = send_message_v2(bot_userid, channel_url, sender, prompts[1])
                response = send_message_v2(bot_userid, channel_url, sender, prompts[0])
            else:
                response = send_message_v2(bot_userid, channel_url, sender, prompts)
        if images and files:
            response = send_message_v2(bot_userid, channel_url, sender, files)
            click_here_to_send_file_via_email(bot_userid, channel_url, sender, email_trace + attachment_mapper_swapped(files['cards'][0]['buttons'][0]['link']))
            response = send_message_v2(bot_userid, channel_url, sender, images)
            if did_i_answer_your_question_flag:did_i_answer_your_question(bot_userid, channel_url, sender)
            images, files = [], []
        if images:
            response = send_message_v2(bot_userid, channel_url, sender, images)
            if did_i_answer_your_question_flag:did_i_answer_your_question(bot_userid, channel_url, sender)
        if files:
            response = send_message_v2(bot_userid, channel_url, sender, files)
            click_here_to_send_file_via_email(bot_userid, channel_url, sender, email_trace + attachment_mapper_swapped(files['cards'][0]['buttons'][0]['link']))
            if did_i_answer_your_question_flag:did_i_answer_your_question(bot_userid, channel_url, sender)
        return response

def sending_email(bot_userid, channel_url, sender):
    hr_email_flag_2 = find_three_consecutive_not_found(users_chat_data_holder[sender].__dict__['chat_log'])
    if hr_email_flag_2:
        send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_no_flow_message)))
        send_message_v2(bot_userid, channel_url, sender, wf_format.message_format(random.choice(config.default_mail_flow_final_message)))
        
        user_data = [users_chat_data_holder[sender].__dict__] ## ASync Email Push
        
        with concurrent.futures.ThreadPoolExecutor() as executor: 
            futures = executor.map(push_mail, user_data)
        
        try:
            del no_bot_match[sender] ## Remove the user from the loop ##
            del users_chat_data_holder[sender] ## Remove the user from the loop and start collecting fresh logs ##
        except KeyError as e:
            print("error in sending_email", e)
            
        return True
    else:
        return False
    
def postprocess_azure_response_v2(bot_userid, channel_url, sender_id, bot_response, returning_user_data_holder):
  messages, prompt_messages, prompts, images, files, add_fallback = [], [], [], [], [], []
  did_i_answer_your_question_flag = False
#   global returning_user_data_holder
  image_trace = '![image]'
  file_trace = '![file]'
  chitchat_trace = ['qna_chitchat_Professional.tsv', 'qna_chitchat_professional.tsv', 'qna_chitchat_caring.tsv', 'qna_chitchat_Caring.tsv', 'qna_chitchat_enthusiastic.tsv', 'qna_chitchat_Enthusiastic.tsv', 'qna_chitchat_friendly.tsv', 'qna_chitchat_Friendly.tsv', 'qna_chitchat_witty.tsv', 'qna_chitchat_Witty.tsv']
  
  welcome_messages_from_bot = ['Hello.', 'Hi!', 'Hello there!', 'Hey.','Hello, I am (HCM Bot)!, How can I help you ?']
  custom_flow_identifier = ['Great! Is there anything else I can help you with today ?', 'Before you go how would you rate my service?']
  if config.debug:
      print("bot_response", bot_response)
      pass
  
  ## IF no matching or no good answers found in KB
  for i in bot_response['answers']:
      if(i['answer'] == 'No good match found in KB.' or i['score'] == 0.0 or i['questions'] == [] or i['id'] == -1):
          
          ## Increase the counter for sending the mail
          try:
              no_bot_match[sender_id] += 1
          except KeyError:
              no_bot_match[sender_id] = 1
            
          count = no_bot_match[sender_id]
          
          if count >= config.threshold:
              if(sending_email(bot_userid, channel_url, sender_id)):
                  outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages, prompts), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
                  return outputs
              else:
                  messages.append(random.choice(config.default_fallback_answer))
                  outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages, prompts), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
                  return outputs
          
          messages.append(random.choice(config.default_fallback_answer))
          outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages, prompts), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
          return outputs
      
  ## If it's a custom flow message
  for i in bot_response['answers']:
      if(i['answer'] in custom_flow_identifier):
        if(bot_response['answers'][0]['context']['prompts']):
            if i['answer'] == custom_flow_identifier[0]:
                prompt_messages.append(random.choice(config.default_custom_flow_questions))
            else:
                prompt_messages.append(bot_response['answers'][0]['answer'])
            for prompt in (bot_response['answers'][0]['context']['prompts']):
                prompts.append(prompt['displayText'])
            outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages, prompts), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
            return outputs
      
  ## If it's a greeting message, send a custom greeting response
  for i in bot_response['answers']:
      if(i['answer'] in welcome_messages_from_bot):
          if sender_id not in returning_user_data_holder:
              messages.append(random.choice(config.default_welcome_answer_first_time))
              returning_user_data_holder.append(sender_id)
              returning_user_data_holder = list(set(returning_user_data_holder))
          else:
              messages.append(random.choice(config.default_welcome_answer_second_time))
          outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages, prompts), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
          return outputs
        
  ## IF good answers found in KB
#   if(len(bot_response['answers']) == 1):
  if(len(bot_response['answers']) == 1 and bot_response['answers'][0]['score'] >= config.score_threshold):
    if(image_trace in bot_response['answers'][0]['answer'] and file_trace in bot_response['answers'][0]['answer']):
        if(bot_response['answers'][0]['answer'].split(image_trace)[0] != "" and bot_response['answers'][0]['answer'].split(file_trace)[0] != ""):
            messages.append(bot_response['answers'][0]['answer'].split(image_trace)[0])
            images.append(bot_response['answers'][0]['answer'].split(image_trace + '(')[-1].split(')')[0])
            files.append(bot_response['answers'][0]['answer'].split(file_trace + '(')[-1].split(')')[0])
            did_i_answer_your_question_flag = True
    elif(image_trace in bot_response['answers'][0]['answer']):
        if bot_response['answers'][0]['answer'].split(image_trace)[0] != "":
            messages.append(bot_response['answers'][0]['answer'].split(image_trace)[0])
            images.append(bot_response['answers'][0]['answer'].split('(')[-1].split(')')[0])
            did_i_answer_your_question_flag = True
    elif(file_trace in bot_response['answers'][0]['answer']):
        if bot_response['answers'][0]['answer'].split(file_trace)[0] != "":
            messages.append(bot_response['answers'][0]['answer'].split(file_trace)[0])
            files.append(bot_response['answers'][0]['answer'].split('(')[-1].split(')')[0])
            did_i_answer_your_question_flag = True
    elif(bot_response['answers'][0]['context']['prompts']):
        prompt_messages.append(bot_response['answers'][0]['answer'])
        for prompt in (bot_response['answers'][0]['context']['prompts']):
            prompts.append(prompt['displayText'])
    else:
        messages.append(bot_response['answers'][0]['answer'])
        did_i_answer_your_question_flag = True
        if(bot_response['answers'][0]['source'] in chitchat_trace):
            did_i_answer_your_question_flag = False
        if(bot_response['answers'][0]['answer'] in config.user_comments_trace):
            users_comments_collector[sender_id] = ""
            did_i_answer_your_question_flag = False
  else:
    for i in (bot_response['answers']):
        if(int(i['score']) == int(100)):
            if(image_trace in i['answer'] and file_trace in i['answer']):
              messages.append(i['answer'].split(image_trace)[0])
              images.append(i['answer'].split(image_trace + '(')[-1].split(')')[0])
              files.append(i['answer'].split(file_trace + '(')[-1].split(')')[0])
            elif(image_trace in i['answer']):
              messages.append(i['answer'].split(image_trace)[0])
              images.append(i['answer'].split(image_trace + '(')[-1].split(')')[0])
            elif(file_trace in i['answer']):
              messages.append(i['answer'].split(file_trace)[0])
              files.append(i['answer'].split(file_trace + '(')[-1].split(')')[0])
            else:
              messages.append(i['answer'])
              
            if(i['source'] not in chitchat_trace):
                did_i_answer_your_question_flag = True
            for prompt in (i['context']['prompts']):
                prompts.append(prompt['displayText'])
                did_i_answer_your_question_flag = False
                messages = []
            prompt_messages.append(i['answer'])
            break
        else:
            if(i['source'] not in chitchat_trace):
                if i['source'] not in ['Editorial']: # This will prevent the option driven based answers from being shown as recommendations to the user. Beware do not add new primary questiosn in the editorial section, because they are never shown as recommendations, so use a new file to upload and maintain.
                    prompts.append(i['questions'][0]) # Don't accumulate all the primary and alternative questions into prompts section to the user. As requested just the primary question must take part in the prompt area
                add_fallback = [random.choice(config.default_fallback_question)] ## Add default fallback question
            elif i['source'] in chitchat_trace:
                messages.append(i['answer'])
  outputs = holder._make([ wf_format.message_format(messages), wf_format.prompt_messages_format(prompt_messages,  prompts + add_fallback), wf_format.image_format(images), wf_format.file_format(files), did_i_answer_your_question_flag ])
  return outputs

def send_message_v2(bot_userid, channel_url, recipient_id, message_payload, save_log = True):
    payload_part_1 = {
        "bot_userid" : bot_userid,
        "channel_url" : channel_url
    }
    payload_part_2 = message_payload
    print("Composed Payload >>>", payload_part_1 | payload_part_2)
    response = requests.request("POST", WORKVIVO_API_URL, data=json.dumps(payload_part_1 | payload_part_2), headers=headersList)
    bot_chat_timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d %H:%M:%S"))
    
    if save_log:
        try:
            users_chat_data_holder[recipient_id].store_logs(recipient_id, bot_chat_timestamp + " - " + str(payload_preprocess(message_payload))) ## Log bot's message ##
        except KeyError:
            pass
        
    return response.json()

def did_i_answer_your_question(bot_userid, channel_url, sender):
    buttons = []
    buttons.append({"label":"< Yes >","message":"< Yes >"})
    buttons.append({"label":"< No >","message":"< No >"})
    payload = {"type": "card", "cards": [{"cardTitle": random.choice(config.default_did_I_answer_your_question), "cardDescription": "", "cardImage": "https://synapxe.workvivo.com/document/link/83872", "buttons": buttons}]}
    send_message_v2(bot_userid, channel_url, sender, payload)

def new_hire_prompt(sender):
    buttons, buttons_holder = [], []
    buttons.append({"type":"postback","title":"yes","payload":"What is my Annual Leave entitlement?"})
    buttons.append({"type":"postback","title":"no","payload":list(new_hire_trace.keys())[0]})
    buttons_holder.append({"title": "Would you like to know our annual leave benefit?", "buttons":buttons})
    send_message_v2(sender, {"attachment":{"type":"template","payload":{"template_type":"generic", "elements": buttons_holder}}})

def click_here_to_send_file_via_email(bot_userid, channel_url, sender, attachment_id):
    return False ## Disable this line to enable this function
    buttons = [{"label":"Yes, email me","message":attachment_id}]
    payload = {"type": "card", "cards": [{"cardTitle": random.choice(config.default_email_sending_question), "cardDescription": "", "cardImage": "https://synapxe.workvivo.com/document/link/83872", "buttons": buttons}]}
    send_message_v2(bot_userid, channel_url, sender, payload)

def payload_preprocess(payload):
  try:
    try:
      return "Bot : " + payload['text']#.split("(http")[0]
    except:
      if (payload['attachment']['type'] == 'image'):
        # return "Image id : " + str(payload(['attachment']['payload']['attachment_id']))
        return "Image id : " + str(payload['attachment']['payload']['attachment_id'])
      elif (payload['attachment']['type'] == 'template'):
          try:
              return "Bot : " + str(payload['attachment']['payload']['elements'][0]['title'])
          except:
              return "Bot : " + str(payload['attachment']['payload']['text'])
  except:
    return "Bot : " + str(payload)
 
def mask_urls_remove_https(text):
    url_pattern = r'https?://\S+'
    
    def replacer(match):
        url = match.group(0)
        # Remove https:// and replace . with [dot]
        url = url.replace('https://', '').replace('http://', '').replace('.', '[dot]')
        return url

    return re.sub(url_pattern, replacer, text)

def email_data_formatting(message_content, user_details):
    print("email_data_formatting inputs", message_content, user_details)

    text = ""
    text += "** USER DETAILS **\n"
    text += str(user_details)
    # for k,v in user_details.items():
    #     text += k + " : " + v + "\n"
    text += "\n\n"
    
    text += "** CHAT LOGS **\n"
    
    index_to_track = 0
    indexs_holder = []
    for message in message_content['chat_log']:
        if any(sm in message for sm in special_messages[0:2]):
            indexs_holder.append(message_content['chat_log'].index(message))
    if(indexs_holder):
        index_to_track = min(indexs_holder) - 3
    
    message_content_formatted = message_content['chat_log'][index_to_track:] ## Send only a small portion of the chat logs from where the user has said No to the question.
    message_content_formatted = [item.replace('User : < No >', 'User : No') for item in message_content_formatted]
    
    for item in message_content_formatted:
        text += item + " \n "
    return mask_urls_remove_https(text)

def get_workvivo_user_data(sender_id):
    ## Get User's Details with error handling ##
    try:
        user_data = workvivo_utils.get_user_data(sender_id)
        return user_data
    except KeyError:
        return {'name': 'Praveen R', 'id': sender_id, 'email': 'praveen.r@spritle.com'}
    
def push_mail(data):
    try:
        # user_data = fb_workplace.get_user_data(data['sender_id'])
        # user_data = get_workvivo_user_data(data['sender_id'])
        print("push_mail >>>", data)
        user_data = data['sender_id']
        mail_service.sendEmail("ChatBot Query", str(email_data_formatting(data, user_data)))
        
        timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d"))
        query = "INSERT INTO user_escalations (date, user_id) VALUES (%s, %s)"
        argument = (timestamp, data['sender_id'])
        db_utils.insert_data_to_db(query, argument)
    except Exception as e:
        print(e)
        print("Error in sending email")
    return True

def push_mail_with_attachment(data):
    try:
        # user_data = get_workvivo_user_data(data['sender_id'])
        user_data = data['sender_id']
        mail_service.sendEmailWithAttachment(user_data, data['attachment_id'])
    except Exception as e:
        print(e)
        print("Error in sending email with attachment")

def collect_comments_and_rating(sender, comment, rating):
    timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d"))
    query = "INSERT INTO user_comments (date, user_id, rating, comments) VALUES (%s, %s, %s, %s)"
    argument = (timestamp, sender, str(rating).split(':')[-1].strip(), str(comment))
    db_utils.insert_data_to_db(query, argument)

def find_three_consecutive_no(chat_log, catch_phrases = special_messages[0:2]):
  occurences = []
  for i,o in enumerate(chat_log):
    for catch_phrase in catch_phrases:
      if catch_phrase in o:
        occurences.append(i)
  differences = sum(np.diff(occurences)[-2:])
  if differences > 0 and differences < 20:
    return True
  else:
    return False

def find_three_consecutive_not_found(chat_log, catch_phrases = config.default_fallback_answer):
  occurences = []
  threshold = 2
  for i,o in enumerate(chat_log):
    for catch_phrase in catch_phrases:
      if catch_phrase in o:
        occurences.append(i)
  differences = sum(np.diff(occurences)[-2:])
  if differences > 0 and differences < 5 and len(occurences) >= threshold:
    return True
  else:
    return False

def welcome_new_hires():    
    users_to_trigger_list = ["rebecca.low@ihis.com.sg", "REESHMINI.VIJEYAKUMAR@IHIS.COM.SG"]
    users_to_trigger_dict = {}    
    all_fb_users = fb_workplace.get_all_user_id()
    email_to_user_id_mapper = {}
    for user in all_fb_users:
        email_to_user_id_mapper[user['email']] = user['id']
    # users_to_trigger = {'balakrishnav': '100077347014829'}
    
    for user_to_trigger in users_to_trigger_list:
        user_to_trigger = user_to_trigger.lower().strip()
        user_id = email_to_user_id_mapper.get(user_to_trigger, None)
        if user_id:
            users_to_trigger_dict[user_to_trigger] = user_id
        else:
            print("user_id not available for : {}".format(user_to_trigger))
    new_hires = list(users_to_trigger_dict.values())
    print("new_hires : {}".format(new_hires))
    
    for new_hire in new_hires:
        send_message_v2(new_hire,  wf_format.message_format(random.choice(config.default_new_hire_welcome_message)))
        new_hire_prompt(new_hire)
        time.sleep(3)
        
# scheduler = BackgroundScheduler(timezone=config.timezone)
# scheduler.start()
# scheduler.add_job(
#     welcome_new_hires, 
#     'date', 
#     run_date=datetime.datetime(2022, 9, 6, 9, 1, 1)
#     )