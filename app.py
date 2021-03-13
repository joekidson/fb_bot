#Python libraries that we need to import for our bot
import random
import os
from src import yes_path, undecided_path
from flask import Flask, request
from pymessenger.bot import Bot
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
bot = Bot(ACCESS_TOKEN)

with open('data/question_paths.json') as json_file:
    questions_paths = json.load(json_file)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                try:
                    convo_data = read_json_object(message)
                except Exception:
                    convo_data = {
                        'id': recipient_id,
                        'details': {
                            'voting': None,
                            'name': None
                        },
                        'conversation_history': [],
                        'current_conversation': ['going_to_vote', '1']
                    }
                    q_path = convo_data['current_conversation'][0]
                    q_num = convo_data['current_conversation'][1]
                    response_sent_text = questions_paths[q_path][q_num]['bot_text']
                    send_message(recipient_id, response_sent_text)
                    convo_data['conversation_history'].append({
                        'from': 'bot',
                        'text': response_sent_text
                    })
                    write_json_obj(message, convo_data)
                    return "Message Processed"

                if message['message'].get('text'):
                    q_path = convo_data['current_conversation'][0]
                    q_num = convo_data['current_conversation'][1]
                    question_p = questions_paths[q_path][q_num]
                    v_res = question_p['valid_responses']

                    response_sent_text = message['message'].get('text')
                    convo_data['conversation_history'].append({
                        'from': 'person',
                        'text': response_sent_text
                    })

                    clean_res = response_sent_text.replace(" ", "").lower()
                    if clean_res in v_res:
                        convo_data['details'][question_p['to_write']] = response_sent_text
                        next_q = question_p['goto'][clean_res]
                        q_path = next_q[0]
                        q_num = next_q[1]
                        response_sent_text = questions_paths[q_path][q_num]['bot_text']
                        send_message(recipient_id, response_sent_text)
                        convo_data['current_conversation'] = next_q
                        convo_data['conversation_history'].append({
                            'from': 'bot',
                            'text': response_sent_text
                        })
                        write_json_obj(message, convo_data)
                    else:
                        response_sent_text = question_p['valid_res_explainer']
                        send_message(recipient_id, response_sent_text)
                        convo_data['conversation_history'].append({
                            'from': 'bot',
                            'text': response_sent_text
                        })
                        response_sent_text = question_p['bot_text']

                        send_message(recipient_id, response_sent_text)
                        convo_data['conversation_history'].append({
                            'from': 'bot',
                            'text': response_sent_text
                        })

                        write_json_obj(message, convo_data)

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def read_json_object(obj):
    file_name = '{}_chat_log.json'.format(obj['sender']['id'])
    path = 'data/{}'.format(file_name)
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def write_json_obj(obj, data):
    file_name = '{}_chat_log.json'.format(obj['sender']['id'])
    path = 'data/{}'.format(file_name)
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    app.run()
