import time, random, json, os, datetime, pytz
import utility.config as config
from flask_wtf import FlaskForm
from wtforms.fields import DateField, IntegerField
from wtforms.validators import Optional
from wtforms import validators, SubmitField
import utility.db_utils as db_utils
from utility.attachments import attachment_mapper

class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=[Optional(),])
    enddate = DateField('End Date', format='%Y-%m-%d', validators=[Optional(),])
    days = IntegerField('Days', validators=[validators.Optional(),])
    submit = SubmitField('Submit')
  

class WORKVIVO_FORMATTER:
  def __init__(self):
    pass

  def message_format(self, messages):
    if messages:
      complete_message = ""
      for message in messages:
        complete_message += message
      return {"type": "message", "message": complete_message}
    return False

  def prompt_messages_format(self, prompt_messages, prompts): 
    print("prompt_messages", prompt_messages, prompts)
    if prompt_messages or prompts:
      complete_message = ""
      buttons = []
      generic_replies = True
      
      for message in prompt_messages:
        complete_message += message
      if complete_message == "":
        complete_message += random.choice(config.default_prompt_message)
        
      if len(prompts) < 1 or prompts == ['Yes', 'No'] or prompts == ['ZEVIGOSOLUTIONSSEY', 'ZEVIGOSOLUTIONSON']:
        if prompts == ['ZEVIGOSOLUTIONSSEY', 'ZEVIGOSOLUTIONSON']:
          mapper = {'ZEVIGOSOLUTIONSSEY':'Yes', 'ZEVIGOSOLUTIONSON':'No'}
          buttons = [{"label":mapper[str(prompt)],"message":str(prompt)} for prompt in prompts]
          return {"type": "card", "cards": [{"cardTitle": complete_message, "cardDescription": "", "cardImage": "https://synapxe.workvivo.com/document/link/77793", "buttons": buttons}]}
        # else:
        #   buttons = [{"label":str(prompt),"message":str(prompt)} for prompt in prompts ]
        #   return {"type": "card", "cards": [{"cardTitle": complete_message, "cardDescription": "", "cardImage": "", "buttons": buttons}]}
      
      elif(generic_replies.__eq__(True)):
        for index, prompt in enumerate(prompts):
          buttons.append({"message":str(prompt),"label":str(prompt)})
        
        if len(buttons) > 10:
          buttons = buttons[0:9] + buttons[-1:] # Limit to 10 carousels only to adhere facebook workplace limitation
        return {"type": "card", "cards": [{"cardTitle": complete_message, "cardDescription": "", "cardImage": "https://synapxe.workvivo.com/document/link/77793", "buttons": buttons}]}
    return False

  def image_format(self, images):
    """
    Image format - https://developers.facebook.com/docs/messenger-platform/send-messages/#types
    """
    if images:
      for image_id in images:
        return {
          "type": "card",
          "cards": [
            {
              "cardTitle": "Please click the button to view the image",
              "cardDescription": "",
              "cardImage": "https://synapxe.workvivo.com/document/link/77793",
              "buttons": [
                {'label': 'Image File', 'link': attachment_mapper(image_id, "image")}
              ]
            }
          ]
        }
    return False
  
  def file_format(self, files):
    if files:
      for file_id in files:
        return {
          "type": "card",
          "cards": [
            {
              "cardTitle": "Please click the button to view the file",
              "cardDescription": "",
              "cardImage": "https://synapxe.workvivo.com/document/link/77791",
              "buttons": [
                {'label' : 'File', 'link' : attachment_mapper(file_id, "file")}
              ]
            }
          ]
        }
    return False
  

class DATA_COLLECTOR:
    def __init__(self, sender_id = None, chat_log = [], timestamps = []):
      self.sender_id = sender_id
      self.chat_log = chat_log
      self.timestamps = timestamps
      self.user_sleep_timer_threshold = int(config.user_sleep_timer) * 60 # Mins to clear chat and start afresh

    def store_logs(self, sender_id, chat):
      assert sender_id == self.sender_id, 'Sender Mismatch'
      self.timestamps.append(int(time.time()))
      self.timestamps = self.timestamps[-2:]
      self.check_timer()

      self.chat_log.append(chat)
      # self.chat_log = self.chat_log[-5:]
    
    def check_timer(self):
      if self.timestamps and len(self.timestamps) >= 2:
        previous, current = self.timestamps[-2], self.timestamps[-1]
        if((current - previous) > self.user_sleep_timer_threshold):
          print("cleaning chat_logs")
          self.chat_log = []
        
        
def batch(iterable, n = 1):
  current_batch = []
  for item in iterable:
    current_batch.append(item)
    if len(current_batch) == n:
      yield current_batch
      current_batch = []
  if current_batch:
    yield current_batch
    
class USER_DATA:
  def __init__(self, name, id, email):
    self.name = name
    self.id = id
    self.email = email
        
class azure_bot_cache_v2:
  def __init__(self) -> None:
    os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)
        
    ## overall cache
    try:
      with open(config.cache_path) as f:
        self.cache = eval(f.read())
    except FileNotFoundError:
      self.cache = {}
      with open(config.cache_path, "w") as outfile:
        outfile.write(json.dumps(self.cache))
    
    self.user_cache_logs_holder = []
        
  def get_from_cache(self, question, userId):
    resp = self.cache.get(question.lower(), None)
    
    if resp:
      self.save_user_cache(question, userId)
      return resp
    return resp
  
  def save_user_cache(self, question, userId):
    timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d"))
    datestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%H:%M:%S"))
    self.user_cache_logs_holder.append([timestamp, datestamp, userId, question])
    
    if len(self.user_cache_logs_holder) % int(config.save_user_cache_for_every) == 0:
      for data in self.user_cache_logs_holder:
        db_utils.insert_data_into_db_user_cache_logs(data)
      self.user_cache_logs_holder = []
      return
    else:
      return

  def save_to_cache(self, question, answer):
    if question not in list(self.cache.keys()):
      self.cache[question] = answer
        
    if len(self.cache) % int(config.save_cache_for_every) == 0:
      with open(config.cache_path, "w") as outfile:
        outfile.write(str(self.cache))