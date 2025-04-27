import requests, json
import utility.config as config
import utility.datastructures as datastructures

cache_mechanism = datastructures.azure_bot_cache_v2()

def transform_to_qnamaker_format(data):
    if not data or not isinstance(data, dict) or 'answers' not in data:
        return data
    
    transformed_answers = []

    for answer in data['answers']:
        new_answer = answer.copy()    
        if 'confidenceScore' in new_answer:
            new_answer['score'] = round(new_answer.pop("confidenceScore")*100,2)
        if 'dialog' in new_answer:
            new_answer['context'] = new_answer.pop('dialog')
        transformed_answers.append(new_answer)
    return {"answers": transformed_answers}


def azure_bot_response(user_question, userId = "Zevigo Middleware"):
    if config.use_cache:
        cache_resp = cache_mechanism.get_from_cache(user_question, userId)
        if cache_resp:
            return cache_resp
    Headers = { "Authorization" : config.azure_bot_authorization_token, "Content-Type" : "application/json" }
    payload = {"question": user_question, "top": config.maximum_suggestions, "scoreThreshold": config.score_threshold, "userId" : userId }
    azure_bot_response = json.loads(requests.post(config.azure_bot_url, headers = Headers, json = payload).text)
    cache_mechanism.save_to_cache(user_question.lower(), azure_bot_response)
    return azure_bot_response


def azure_bot_response_cqa(user_question, userId = "Zevigo Middleware"):
    # if config.use_cache:
    #     cache_resp = cache_mechanism.get_from_cache(user_question.lower(), userId)
    #     if cache_resp:
    #         return cache_resp
    Headers = { "Ocp-Apim-Subscription-Key" : config.azure_bot_authorization_token, "Content-Type" : "application/json" }
    payload = {"question": user_question, "top": config.maximum_suggestions, "confidenceScoreThreshold": config.suggestions_threshold, "userId" : userId }
    azure_bot_response = transform_to_qnamaker_format(json.loads(requests.post(config.azure_bot_url, headers = Headers, json = payload).text))
    # cache_mechanism.save_to_cache(user_question.lower(), azure_bot_response)
    return azure_bot_response

# question = 'medical leave'
# a_resp = azure_bot_response(question)
# print("")
# print(a_resp)

# import logging
# from logging.handlers import RotatingFileHandler
# logging.basicConfig(level=logging.INFO, 
#                     handlers=[RotatingFileHandler("./logs/utils.log", maxBytes=10000000)],
#                     format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s")
