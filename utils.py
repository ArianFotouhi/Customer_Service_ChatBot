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

def cancel_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt,additional_note):

        body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
        sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
        sender.EmailSender(subject = "Request Submission: Cancelation ", body = body)
#email to user as well
        return 'Your cancelation request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'


def refund_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    
    body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
    sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
    sender.EmailSender(subject = "Request Submission: Refund", body = body)
    
    return 'Your refund request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'

def amend_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    
    body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
    sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
    sender.EmailSender(subject = "Request Submission: Amendment ", body = body)
    
    return 'Your amending request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'

def qr_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    
    body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
    sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
    sender.EmailSender(subject = "Request Submission: Not received QR code ", body = body)

    return 'Your QR sending request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'

def dispute_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    
    body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
    sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
    sender.EmailSender(subject = "Request Submission: Dispute ", body = body)
    
    return 'Your dispute request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'

def inquiry_service(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    
    body = email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note)
    sender = EmailNotif.email_notif(sender_address= sender_email_address, sender_password= sender_email_password, recipient_email=recpeint_email_address)
    sender.EmailSender(subject = "Request Submission: Inquiry ", body = body)
    
    return 'Your inquiry request has been received. We will contact you accordingly and in case of further inquries please email info@company.com'

function_descriptions_multiple = [
    {
        "name": "cancel_service",
        "description": "To make service cancelation request, it assumes account details are already received. The function will show a form receiving request details",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    }, 
    {
        "name": "refund_service",
        "description": "To create a refund request",
        "parameters": {
            "type": "object",
            "properties": {          
            },
            "required": [],
        },
    },
    {
        "name": "amend_service",
        "description": "Creating amendment request that changes the date of reservation of service",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    },
    {
        "name": "qr_service",
        "description": "When QR code is not sent to the user",
        "parameters": {
            "type": "object",
            "properties": {          
            },
            "required": [],
        },
    },
    {
        "name": "dispute_service",
        "description": "To create dispute request",
        "parameters": {
            "type": "object",
            "properties": {          
            },
            "required": [],
        },
    },
    {
        "name": "inquiry_service",
        "description": "To send the company an inquiry",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    },

    ]
def db_chat_history_func(chat_id, max_retrieve=20):
    db = ChatDatabase()
    db.create_table()

    output = db.fetch_table(query=f'''SELECT user_message, bot_response, datetime
    FROM chat_history
    WHERE chat_id = '{chat_id}'
    ORDER BY datetime DESC
    LIMIT {max_retrieve};
    ''')
                    
    history = []
    for i in output:
        history.append({'human_user': i[0], 'customer_service_bot': i[1], 'datetime': i[2]})

    return history
# history = []

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

def request_manager(chat_history, ref_num, start_dt, book_start_dt,
                     life_mile_cert,lounge_name,email_addr,first_name,
                     last_name,new_dt, additional_note, req_type):

        chat_id = session['chat_id']

        record = {
            'chat_id': chat_id,
            'ref_num': ref_num,
            'start_dt': start_dt,
            'book_start_dt': book_start_dt,
            'life_mile_cert': life_mile_cert,
            'lounge_name': lounge_name,
            'new_dt': new_dt,
            'additional_note': additional_note,
            'first_name': first_name,
            'last_name': last_name,
            'email_addr': email_addr,
            'req_sub_datetime': datetime.now(),
            'request_type': req_type
        }

        #put it into the db_manager
        db_manager(record_type = 'request', **record)

def email_content(ref_num, start_dt, book_start_dt, life_mile_cert,lounge_name,email_addr,first_name,last_name,new_dt, additional_note):
    body = 'A request has been submitted.'
    
    if ref_num:
        body += '\n Reference Number: '+str(ref_num)
    if start_dt:
        body += '\n Service Start Date: '+str(start_dt)
    if book_start_dt:
        body += '\n Service Booking Date: '+str(book_start_dt)
    if life_mile_cert:
        body += '\n Life Mile Certificate: '+str(life_mile_cert)
    if life_mile_cert:
        body += '\n Lounge Name: '+str(lounge_name)
    if email_addr:
        body += '\n Email Address: '+str(email_addr)
    if first_name:
        body += '\n First Name: '+str(first_name)
    if last_name:
        body += '\n Last Name: '+str(last_name)
    if new_dt:
        body += '\n New Selected Date: '+str(new_dt)
    if additional_note:
        body += '\n Additional Note: '+str(additional_note)

    return body



def create_chat_id():
        return str(uuid.uuid4())
