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

def cancel_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt):

        print('cancelation inputs:')
        print(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt)
#           sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
#           sender.EmailSender(subject = "Request Submission: Cancelation ", body = body)

        return 'Your request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'




def refund_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt):
    
    print('refund inputs:')
    print(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt)
    
    return 'Your request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'


function_descriptions_multiple = [
    {
        "name": "cancel_service",
        "description": "To cancel the service, it assumes account details are already received. Only cancelation reason should be received in prompt.",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    }, 
    {
        "name": "refund_service",
        "description": "To create refund request",
        "parameters": {
            "type": "object",
            "properties": {          
            },
            "required": [],
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
