from flask import session
import uuid
from sentiment_analyzer import analyzer
from config import my_api_key, model_name
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from datetime import datetime
from config import users, sender_email_address, sender_email_password, recpeint_email_address

import uuid
from sentiment_analyzer import analyzer
from bot_db import ChatDatabase, RequestDatabase
from NotifPy import EmailNotif

llm = ChatOpenAI(model=model_name, temperature = 0, openai_api_key = my_api_key)


def cancel_service(reason):
        # make the confirmation form present (or a confirmation pop up)
        # grab the selected option
        # make the confirmation form disappeared
        #confirmation = request.json['confirmation']
        print('reason in cancel func', reason)
        confirmation= 'yes'
        if confirmation.lower() == 'yes':
            request_manager(history, 'cancelation')
            
            username = session['username']
            body = f'''A cancelation request is submitted by:
            
            Username: {username}
            First Name: {users[username]['first_name']}
            Last Name: {users[username]['last_name']}
            Email: {users[username]['email']}
            Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            '''
            sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
            sender.EmailSender(subject = "Request Submission: Cancelation ", body = body)

            return 'Please click on the link https://company.com/cancelation, and also please email to cancel@company.com in case of further assistance.'

        else:

            return 'Cancelation request is annuled by the user'

def extend_service(extension_period):

    ans = 'yes'
    if ans.lower() == 'yes':
        username= session['username']

        body = f'''A service extension request is submitted by:
        
        Username: {username}
        First Name: {users[username]['first_name']}
        Last Name: {users[username]['last_name']}
        Email: {users[username]['email']}
        Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        '''
        sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
        sender.EmailSender(subject = "Request Submission: Extension ", body = body)

        return f'Please click on the link https://company.com/extend, and also please email to extend@company.com in case of further assistance.'

    elif ans.lower() == 'no':
        return 'The request is canceled for service extension'
    
    else:
        ans = input(f'How many months extend? Also you can cancel by saying quit')
        if ans.lower() == 'quite':
            return 'The request is canceled for service extension'             

        else:
            return f'Service extended for {extension_period} months. Please email extend@company.com in case of further inqueries'

def refund(refund_reason, refund_amount, reference_num):
    ans = 'yes'

    if str(reference_num).isdigit():    
        if ans.lower() == 'yes':
            username= session['username']
            print('reference_num:', reference_num)
            print('refund_amount', refund_amount)
            print('refund_reason', refund_reason)
            body = f'''A refund request is submitted by:
            
            Username: {username}
            First Name: {users[username]['first_name']}
            Last Name: {users[username]['last_name']}
            Email: {users[username]['email']}
            Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            '''
            sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
            sender.EmailSender(subject = "Request Submission: Refund ", body = body)

        else:
            return 'Refund request canceled'
    
    else:
        return 'Refund request failed to submit. Please create a request including reference number'

    return 'Please click on the link https://company.com/refund, and also please email to refund@company.com in case of further assistance.'


function_descriptions_multiple = [
    {
        "name": "cancel_service",
        "description": "To cancel the service, it assumes account details are already received. Only cancelation reason should be received in prompt.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "This is the reason of cancelation",
                },
            },
            "required": ["reason"],
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
                "reference_num": {
                    "type": "string",
                    "description": "Reference number to find the purchase information, it should be provided in user message not generated by system",
                },
                
            },
            "required": ["refund_reason","refund_amount","reference_num"],
        },
    },
    ]
history = []


def db_manager(record_type,**record):
        #records is list of dictionaries
        if record_type == 'chat':
            db = ChatDatabase()
        elif record_type == 'request':
            db = RequestDatabase()

        db.create_table()
        
        
            #print('in db_mb', r['chat_id'], r['datetime'], r['human_user'], r['customer_service_bot'], r['senti_fl'], r['senti_str'])           
            #db.commit_table(r['chat_id'], r['datetime'], r['human_user'], r['customer_service_bot'], r['senti_fl'], r['senti_str'])
        vals = record.values()
        db.commit_table(*vals)

def chat_manager(chat_history):
        simplified_history = []
        
        for record in chat_history:

            simplified_history.append(record['human_user'])
            simplified_history.append(record['customer_service_bot'])
            
        # determine its sentimental
        sentiment_str , sentiment_fl = analyzer(simplified_history[:2])
        category = llm.predict_messages(
            [
                HumanMessage(content = str(simplified_history)),
                AIMessage(content = 'Return one word (complaint, complement, other) as discussion subject based on the input text'),
                
            ],)

        
        # create list of dictionaries
    
        chat_history[0]['category'] = category.content
        chat_history[0]['senti_fl'] = sentiment_fl
        chat_history[0]['senti_str'] = sentiment_str
    
        #put it into the db_manager
        db_manager(record_type = 'chat', **chat_history[0])

def request_manager(chat_history, request_type):
        if len(chat_history) == 0:
            chat_id = create_chat_id()
        else:
            chat_id = history[0]['chat_id']

        username = session['username']
        first_name = users[username]['first_name']
        last_name = users[username]['last_name']
        email = users[username]['email']
        curr_datetime = datetime.now()
        
        record = {
            'chat_id': chat_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'datetime': curr_datetime,
            'request_type': request_type
        }

        
    
        #put it into the db_manager
        db_manager(record_type = 'request', **record)

def create_chat_id():
        return str(uuid.uuid4())
