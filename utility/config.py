import os, ast

## Set it to False for Titan and True for Pierce
use_cache = True
debug = False

## Pierce - IHIS
# Credentials for Azure
azure_bot_url = os.getenv("AZURE_BOT_URL")

# Sender email for escalations
sender_email = ast.literal_eval(os.getenv("SENDER_EMAIL")) # ["ihis.hcm.enquiries@ihis.com.sg","nans.sgp@gmail.com","praveen.r@spritle.com","balakrishnav@spritle.com"]
    
## Constants
azure_bot_authorization_token = os.getenv("AZURE_BOT_AUTH_TOKEN")
    
## Random Phrases
default_fallback_answer = ["Oops. Let me try again. Could you please rephrase your question?", "Aw shucks, I'm sorry. Try rephrasing your question this time.",	"I'm sorry, let me try again. Please rephrase your question this time."]
default_welcome_answer_first_time = ["Nice to meet you! I am Iris and I have been trained to answer HCM queries. How can I help you today?", "Hello! I am Iris and am trained to help you out with your HCM queries. Ask away!", "Good day! I am Iris, and I can help you with HCM frequently asked questions. What would you like to know?"]
default_welcome_answer_second_time = ["Hi there! How can I help you today?", "Welcome back! What can I do for you?", "How may I assist you today?", "Any questions for me today?"]
default_prompt_message = ["Do you mean any of these?", "Is this what you are looking for?", "Any of these?", "Are you looking for any of these?"]
default_did_I_answer_your_question = ["Did I answer your question?","Was that helpful?","Have I answered your question?","Did I pass?"]
default_custom_flow_questions = ["Great! Is there anything else I can help you with today?","Awesome! Anything else that you may need help with?","That's great! Do you have any other questions?","Is there anything else that I can help you with?","Glad that I could help. Anything else?","Great! Do you have any other questions?"]
default_no_flow_message = ["My apologies. I will get my HCM colleague to get in touch with you.", "Sorry about that. I'll redirect your query to our trusty HCM colleagues."]
default_mail_flow_final_message = ["I look forward to speaking with you again"]
default_comments_response_message = ["I look forward to speaking with you again.","See you around.","Goodbye for now.","Hear from you again.","Have a nice day."]
default_email_sending_question = ["Would you like to receive the file in your inbox?"]
default_mail_sent_message = ["I have sent a copy of the attachment to your inbox via do-not-reply@zevigo.com. You should receive the email shortly."]
default_fallback_question = ["No, I am looking for something else"]
default_new_hire_welcome_message = ["Hi there! Hope your first week/month has been well. I'm Iris and I can help with information on our HCM policies."]
maintenance_message = "Currently I am under maintenance. Please try again after some time. Thanks!!!"
maximum_suggestions = 6
suggestions_threshold = 0.4
score_threshold = 80

## Sendgrid for emails
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

## System Variables
threshold = 3
user_comments_trace = ['Do you have any other comments?']
user_sleep_timer = 15 # Minutes

## Azure Application Insights
# appId = secrets["appId"]
# appKey = secrets["appKey"]

query = """
requests
| where url endswith "generateAnswer"
| project timestamp, id, url, resultCode, duration, performanceBucket
| parse kind = regex url with *"(?i)knowledgebases/"KbId"/generateAnswer"
| join kind= inner (
traces | extend id = operation_ParentId
) on id
| extend question = tostring(customDimensions['Question'])
| extend answer = tostring(customDimensions['Answer'])
| extend score = tostring(customDimensions['Score'])
| extend UserId = tostring(customDimensions['UserId'])
| project timestamp, resultCode, duration, UserId, question, answer, score, performanceBucket,KbId
| where KbId == "58d55f86-4f4c-400f-a43a-63b149b70f45"
| where score != ''
| sort by timestamp
"""

## Email Scheduler Time
timezone = "Asia/Singapore"
day_of_the_week = 'mon'
hour = 8
minute = 30

## Cache Mechanism
cache_path = 'logs/cache.json'
save_cache_for_every = 10
save_user_cache_for_every = 10