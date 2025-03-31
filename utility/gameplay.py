import random, pytz, requests, json, os, string
from datetime import datetime
import utility.config as config
from utility.datastructures import WORKVIVO_FORMATTER
import utility.fb_workplace as fb_workplace
import utility.db_utils as db_utils

alphabets_mapper = {index : item for index, item in enumerate(list(string.ascii_uppercase))}

wf_format = WORKVIVO_FORMATTER()

FB_API_URL = config.graph_api + config._url
VERIFY_TOKEN = config.server_token
PAGE_ACCESS_TOKEN = config.access_token
    
## Load the EXCEL sheet to JSON
def excel_to_json():
  query = "SELECT * FROM quiz_data"
  qna_df = db_utils.read_data_from_db_as_df(query)

  qna_dict = {}
  for index, row in qna_df.iterrows():
    qna_dict[int(index+1)] = {}
    qna_dict[int(index+1)]['question'] = row['question']
    qna_dict[int(index+1)]['options'] = []

    if row['option_1']:
      qna_dict[int(index+1)]['options'].append(row['option_1'])
    if row['option_2']:
      qna_dict[int(index+1)]['options'].append(row['option_2'])
    if row['option_3']:
      qna_dict[int(index+1)]['options'].append(row['option_3'])
    if row['option_4']:
      qna_dict[int(index+1)]['options'].append(row['option_4'])
    
    qna_dict[int(index+1)]['answer'] = qna_dict[int(index+1)]['options'][row['answer'] - 1]
  
  quiz_path = os.path.join(os.getcwd(), "docs", "quiz.json")
  os.makedirs(os.path.join(os.getcwd(), "docs"), exist_ok = True)

  try:
    os.remove(quiz_path)
  except FileNotFoundError:
    pass
  
  with open(quiz_path, 'w') as fp:
    json.dump(qna_dict, fp)
  print("excel_to_json", quiz_path)
  return quiz_path

quiz_json_path = excel_to_json()

def send_message_v2(recipient_id, message_payload):
    payload = {
        'message': message_payload,
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {'access_token': PAGE_ACCESS_TOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
    return response.json()

def send_message_v3(recipient_id, message_payload):
    ## Quick Replies Format
    payload = {
        'message': message_payload,
        'recipient': {
            'id': recipient_id
        },
        'messaging_type': 'RESPONSE'
    }
    auth = {'access_token': PAGE_ACCESS_TOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
            
    return response.json()

class scorer:
  def __init__(self, user_id, total_questions_count):
    self.lot = list(range(1, total_questions_count + 1))
    self.user_data = fb_workplace.get_user_data(user_id)
    self.question_id = []
    self.questions = []
    self.actual_answers = []
    self.user_answers = []
    self.scores = []
    self.timestamps_1 = []
    self.timestamps_2 = []

  def first_half(self, question, question_id, actual_answer):
    self.lot.remove(question_id)
    self.questions.append(question)
    self.question_id.append(question_id)
    self.actual_answers.append(actual_answer)
    self.timestamps_1.append(str(datetime.strftime(datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d %H:%M:%S")))

  def second_half(self, user_answer, score):
    self.user_answers.append(user_answer)
    self.scores.append(score)
    self.timestamps_2.append(str(datetime.strftime(datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d %H:%M:%S")))
  
class gamezone:
  def __init__(self):
    self.gameplay_secret_keyword = ["@trivia", "@TRIVIA", "@Trivia"]
    self.gameplay_trigger_keyword = ["dereggirt yalp em@G"]
    self.encourage_prompts = ["Bingo!:)", "That's correct!", "Very good..", "You're on a roll", "Yup! Next please..", "Good", "You nailed it", "Woohooh", "Going strong…", "I'm impressed", \
                              "Yup yup!", "Cool!", "Spot on", "That's neat"]
    self.gamplay_correct_answer_prompt = "++^^**"
    self.gamplay_wrong_answer_prompt = "~~--=="

    self.submission_message = ["Oh you didn't select the right option. Your game score will be submitted for the contest."]

    self.user_gameplay_stats = {}
    self.user_history = []
    
    self.latest_question_answer = None
    
    with open(quiz_json_path) as user_file:
      self.qna_pair = eval(user_file.read())
  
  @staticmethod
  def make_ordinal(n):
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
  
  def over_and_out(self, user_id):
    ## Remove the user's old scores data if exists and log it before removal
    try:
      ## Data need to be stored here ##
      self.save_game_log(user_id)
      del self.user_gameplay_stats[user_id] ## Remove the user from the loop ##
    except:
      pass
  
  def user_status(self, user_id):
      try:
          self.user_gameplay_stats[user_id]
          return True
      except KeyError as e:
          return False

  def game_initialization(self, user_id, message, override = False):
    if message in self.gameplay_secret_keyword or override:
      
      if not override:
        message_1 = "Welcome to the Ultimate HCM Quiz! \n You only have 1 chance to *select* the right answers to each questions. Game ends when you run out of stamina for correct answers (or when you type a message). *Remember only your first five attempts* at the game will be taken into account for the contest. For full T&Cs, click on the link below."
        send_message_v2(user_id, wf_format.message_format(random.choice([message_1])))

      game_starter_prompt = {
          "text" : "Shall we start ?",
          "quick_replies" : [{"content_type":"text", "title":"Click to start the game!", "payload": random.choice(self.gameplay_trigger_keyword), "image_url" : "https://wallpaperaccess.com/full/1429574.jpg"}, 
                             {"content_type":"text", "title":"No, maybe later", "payload":"Hi", "image_url" : "https://i.imgur.com/aN0RMk4.png"}]
          }
      send_message_v3(user_id, game_starter_prompt)
      
      if not override:
        self.over_and_out(user_id)

      return True
    return False

  def game_question_generator(self, prompt):
    quick_replies = []
    random.shuffle(prompt["options"])
    
    question = ""
    question += prompt["question"] + "\n"
    for index, answer in enumerate(prompt["options"]):
      option_ = "Option {}".format(alphabets_mapper[index])
      question += "\n " + option_ + " : " + str(answer)
      if answer == prompt["answer"]:
        payload = self.gamplay_correct_answer_prompt
        self.latest_question_answer = option_ + " : " + str(prompt["answer"])
      else:
        payload = self.gamplay_wrong_answer_prompt
      quick_replies.append({"content_type":"text", "title": option_, "payload": payload + option_})

    return {"text" : question, "quick_replies" : quick_replies}

  def save_game_log(self, user_id):
    # print("USER CURRENT STATUS - {} & {}".format(user_id, self.user_gameplay_stats[user_id].__dict__))
    # print("USER's ATTEMPT", self.user_history.count(user_id))
    holder = self.user_gameplay_stats[user_id].__dict__
    datestamp = str(datetime.strftime(datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d"))                
    timestamp = str(datetime.strftime(datetime.now(pytz.timezone('Asia/Singapore')), "%H:%M:%S"))
    
    db_utils.insert_data_into_db_save_game_log(datestamp, timestamp, holder['user_data']['id'], len(holder['scores']))

  def game_triggered(self, user_id, message):
    if message in self.gameplay_trigger_keyword:
      self.user_history.append(user_id)
      message_2 = "This is your {} attempt".format(self.make_ordinal(self.user_history.count(user_id)))
      message_3 = "Yes, let's play!"
      send_message_v2(user_id, wf_format.message_format(random.choice([message_2])))
      send_message_v2(user_id, wf_format.message_format(random.choice([message_3])))

      ## Record the user's gameplay here
      self.user_gameplay_stats[user_id] = scorer(user_id, len(self.qna_pair))

      ## Generate Question Format
      first_qna = self.game_question_generator(self.qna_pair["1"])
      send_message_v3(user_id, first_qna)
      self.user_gameplay_stats[user_id].first_half(self.qna_pair["1"]["question"], 1, self.qna_pair["1"]["answer"])
      return True
    return False

  def game_handler(self, user_id, message):
    print("game_handler >>>", user_id, message)
    if message.startswith(self.gamplay_correct_answer_prompt):

      ## Record his score
      self.user_gameplay_stats[user_id].second_half(message[6:], True)

      ## Start generating his next questions      
      try:
        send_message_v2(user_id, wf_format.message_format(random.choice(self.encourage_prompts)))
        next_question_id = str(random.choice(self.user_gameplay_stats[user_id].lot))
        next_qna = self.game_question_generator(self.qna_pair[next_question_id])
        send_message_v3(user_id, next_qna)
        self.user_gameplay_stats[user_id].first_half(self.qna_pair[next_question_id]["question"], int(next_question_id), self.qna_pair[next_question_id]["answer"])
      except IndexError as e:
        ## User has answered all the questions correctly ##
        send_message_v2(user_id, wf_format.message_format(random.choice(["That's phenomenal !!!, you have answered all the questions !!!"])))
        self.over_and_out(user_id)
      return True
    elif message.startswith(self.gamplay_wrong_answer_prompt):
      send_message_v2(user_id, wf_format.message_format(random.choice([self.submission_message])))
      send_message_v2(user_id, wf_format.message_format(random.choice(["The correct answer is " +  "*" + self.latest_question_answer + "*" ])))
      send_message_v2(user_id, wf_format.message_format("Would you like to play again ?"))
      self.over_and_out(user_id)
      self.game_initialization(user_id, "sample message", override = True)
      return True
    else:
      return False

  def gameResponseMain(self, user_id, message):
      
    ## Game init
    if self.game_initialization(user_id, message):
      return True   
    
    ## Request game start permission
    if self.game_triggered(user_id, message):
      return True
    
    ## Continue question cycles
    if self.game_handler(user_id, message):
      return True
    
    return False