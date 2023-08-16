from flask import Flask, render_template, request, jsonify
from bot_db import Database



import json
import openai
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

my_openai_key = "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"
openai.api_key = my_openai_key
memory_length = 20
history = []


def cancel_service():
        # make the confirmation form present (or a confirmation pop up)
        # grab the selected option
        # make the confirmation form disappeared
#        confirmation = request.json['confirmation']
        confirmation= 'yes'
        if confirmation.lower() == 'yes':
            return 'Please click on the link https://company.com/cancelation, and also please email to cancel@company.com in case of further assistance.'
        else:
            return 'Cancelation request is annuled by the user'

def extend_service(extension_period):
    ans = input(f"""please say yes if you request to extend your service for {extension_period} months

                Please note extension is monthly if you want to change number of months say no to this message
                If you want to cancel this request say quit
        """)
    if ans.lower() == 'yes':
        return f'Service extended for {extension_period} months. Please email extend@company.com in case of further inqueries'

    elif ans.lower() == 'no':
        return 'The request is canceled for service extension'
    
    else:
        ans = input(f'How many months extend? Also you can cancel by saying quit')
        if ans.lower() == 'quite':
            return 'The request is canceled for service extension'             

        else:
            return f'Service extended for {extension_period} months. Please email extend@company.com in case of further inqueries'

def refund(refund_reason, refund_amount):
    ans = input(f"""Please say yes if you confirm the reason and amount of refund:
                -Reason:{refund_reason}
                -Amount: {refund_amount}
                
                If any of them are not correct, you can modify by saying no
                If you want cancel refund request, simply say quit
                """)
    
    if ans.lower() == 'yes':
        pass
    elif ans.lower() == 'quit':
        return 'Refund request canceled'
    else:
        refund_reason = input('Refund Reason: ')
        refund_amount = input('Refund Amount: ')

    return 'Your refund request is received. For further inquiries please contact refund@company.com'

function_descriptions_multiple = [
    {
        "name": "cancel_service",
        "description": "To cancel the service, it assumes account details are already received",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    },
    {
        "name": "extend_service",
        "description": "To extend the service",
        "parameters": {
            "type": "object",
            "properties": {
                "extension_period": {
                    "type": "string",
                    "description": "This is the number (number of months) showing period of service extension",
                },
            },
            "required": ["extension_period"],
        },
    },

    {
        "name": "refund",
        "description": "To create refund request",
        "parameters": {
            "type": "object",
            "properties": {
                "refund_reason": {
                    "type": "string",
                    "description": "The reason of refund request",
                },
                "refund_amount": {
                    "type": "string",
                    "description": "The amount of requested refund in CAD (Canadian $)",
                },
            },
            "required": ["refund_reason","refund_amount"],
        },
    },

    ]

llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature = 0, openai_api_key = my_openai_key)

app = Flask(__name__)

# This is a simple dictionary-based chatbot.

def db_mananger(records):
        #records is list of dictionaries
        db = Database()
        db.create_table()
        for r in records:
            print('in db_mb', r['chat_id'], r['datetime'], r['human_user'], r['customer_service_bot'], r['senti_fl'], r['senti_str'])
            db.commit_table(r['chat_id'], r['datetime'], r['human_user'], r['customer_service_bot'], r['senti_fl'], r['senti_str'])

def chat_manager(chat_history):
         
        # determine its sentimental
        sentiment_fl = llm.predict_messages(
            [
                HumanMessage(content = str(chat_history)),
                AIMessage(content = 'return only a float as sentiment analysis result of this chat history from -1 (very negative) to 1 (very positive)'),
                
            ],)
        # determine str sentimental
        try: 
            sentiment_fl = float(sentiment_fl)
            if sentiment_fl.content > 0.1:
                sentiment_str =  'positive'
            elif sentiment_fl.content < - 0.1:
                sentiment_str =  'negative'
            else:
                sentiment_str = 'neutral'
        except Exception as e:
            print('exception in chat_manager', e)
            sentiment_fl = 0.0
            sentiment_str = 'not specified'
        
        # create list of dictionaries
        for record in chat_history:
            record['senti_fl'] = sentiment_fl
            record['senti_str'] = sentiment_str
            print('in CHAT mng', record)
        
        #put it into the db_manager
        db_mananger(chat_history)


def create_chat_id():
        return 1
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
        
        global history
        if len(history) == 0:
            chat_id = create_chat_id()
        else:
            chat_id = history['chat_id']

        user_prompt_ = request.form['user_message']

        system_message = f"""You are a Customer Service Bot. Consider the conversation history in chat:
            history: {history}
            """
        print('history: ', history)

        first_response = llm.predict_messages(
        [HumanMessage(content=user_prompt_),
        
        SystemMessage(content=system_message),],
        functions=function_descriptions_multiple,
        )
 
        if len(history)>memory_length:
            history = history[:memory_length]
        
        try:
            params = first_response.additional_kwargs["function_call"]["arguments"]
            params = params.strip()
            params = json.loads(params)

            chosen_function = eval(first_response.additional_kwargs["function_call"]["name"])
            func_output = chosen_function(**params)
            
            print('func output: ', func_output)
            second_response = llm.predict_messages(
            [
                HumanMessage(content = user_prompt_),
                AIMessage(content = f'the result is: {func_output}, rephrase it and tell it to the customer as her action result'),
            ],
                
            )
            print('second reponse: ', second_response)
            history.insert(0, {'chat_id': chat_id, 'human_user': user_prompt_, 
            'customer_service_bot': func_output,
            'datetime':datetime.now()})
            
            chat_manager(history)
            return jsonify({'response': second_response.content})
        
        except Exception as e:
            print('im in exc')
            print(e)
            
            history.insert(0, {'chat_id':chat_id, 'human_user': user_prompt_, 
            'customer_service_bot': first_response.content, 'datetime':datetime.now()})
            
            chat_manager(history)
            return jsonify({'response': first_response.content})


if __name__ == '__main__':
    app.run(debug=True)
