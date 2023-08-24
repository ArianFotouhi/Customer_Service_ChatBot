from flask import Flask, render_template, request, jsonify, session, redirect
from authentication import Authentication

import json
import openai
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from utils import cancel_service, refund_service, amend_service, qr_service, dispute_service, inquiry_service, create_chat_id, db_manager, request_manager, chat_manager, function_descriptions_multiple, history
from config import users, secret_key, my_api_key, model_name

import traceback

openai.api_key = my_api_key
memory_length = 20

app = Flask(__name__)
app.secret_key = secret_key
authenticate = Authentication().authenticate

llm = ChatOpenAI(model=model_name, temperature=0, openai_api_key=my_api_key)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session["username"] = username
            return redirect('/')
        else:
            return render_template("login.html",
                                   error="Invalid username or password")
    return render_template("login.html")


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')

    func_options = []
    for i in function_descriptions_multiple:
        func_options.append(i['name'])

    return render_template('index.html', func_options=func_options)


@app.route('/get_response', methods=['POST'])
def get_response():
    global history
    if len(history) == 0:
        chat_id = create_chat_id()
    else:
        chat_id = history[0]['chat_id']

    show_button = False
    button_text = None

    # if the form is submitted and we proceed with request submission
    try:
        ref_num = request.form['ref_num']
        start_dt = request.form['start_dt']
        book_start_dt = request.form['book_start_dt']
        life_mile_cert = request.form['life_mile_cert']
        lounge_name = request.form['lounge_name']
        email_addr = request.form['email_addr']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        new_dt = request.form['new_dt']
        additional_note = request.form['additional_note']

        req_type = request.form['req_type']
        if ref_num == '' or start_dt == '' or book_start_dt == '' or lounge_name == '' or email_addr == '' or first_name == '' or last_name == '':
            raise ValueError("Empty value in input")
        params = {
            'ref_num': ref_num,
            'start_dt': start_dt,
            'book_start_dt': book_start_dt,
            'life_mile_cert': life_mile_cert,
            'lounge_name': lounge_name,
            'email_addr': email_addr,
            'first_name': first_name,
            'last_name': last_name,
            'new_dt': new_dt,
            'additional_note': additional_note
        }

        chosen_function = eval(req_type)

        func_output = chosen_function(**params)
        final_reply = func_output
        
        request_manager(history,
                    ref_num, start_dt, book_start_dt,
                    life_mile_cert,lounge_name,email_addr,first_name,
                    last_name,new_dt, additional_note, req_type)
        
        # final_reply = llm.predict_messages(
        #     [
        #         AIMessage(
        #             content=f'the result is: {func_output}, rephrase it and tell it to the customer as their action result.'),
        #     ],)

        history.insert(0, {'chat_id': chat_id,
                           'human_user': f'form submitted for {req_type} request',
                           'customer_service_bot': final_reply,
                           'datetime': datetime.now()})

        chat_manager(history)


        print('I am in Try1')
        return jsonify({'response': final_reply,
                        'buttonText': None})

    # if form is not submitted and we continue with the conversation
    except Exception as e:
        print('exception', e)
        traceback.print_exc()

        user_prompt_ = request.form['user_message']

        system_message = f"""You are a Customer Service Bot. Please ONLY reply questions regarding greeting, service cancelation, extension, refund and aviation industry. Please provide short and easy answers to user prompts. Consider your own conversation history in chat:
                history: {history}
                """

        first_response = llm.predict_messages(
            [
                HumanMessage(content=user_prompt_),
                SystemMessage(content=system_message)
            ],

            functions=function_descriptions_multiple,
        )

        print('I am in Exc1')

    if len(history) > memory_length:
        history = history[:memory_length]

    # A request is about to be submitted (will send the form)
    try:

        chosen_function = eval(
            first_response.additional_kwargs["function_call"]["name"])

        func_output = 'Working on your request...'
        print('func output: ', func_output)
        second_response = llm.predict_messages(
            [
                HumanMessage(content=user_prompt_),
                AIMessage(
                    content=f'the result is: {func_output}, rephrase it and tell it to the customer as their action result.'),
            ],
        )

        print('second reponse: ', second_response)
        history.insert(0, {'chat_id': chat_id, 'human_user': user_prompt_,
                           'customer_service_bot': second_response.content,
                           'datetime': datetime.now()})

        chat_manager(history)
        print('I am in Try2')
        return jsonify({'response': second_response.content,
                        'buttonText': True,
                        'request_type': first_response.additional_kwargs["function_call"]["name"]})
    # It's not about a request
    except Exception as e:

        history.insert(0, {'chat_id': chat_id, 'human_user': user_prompt_,
                           'customer_service_bot': first_response.content, 'datetime': datetime.now()})

        chat_manager(history)
        print('I am in Exc2')
        return jsonify({'response': first_response.content,
                        'buttonText': None,
                        'request_type': None})


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
