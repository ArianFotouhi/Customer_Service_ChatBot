from flask import Flask, render_template, request, jsonify, session, redirect
from authentication import Authentication

import json
import openai
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from utils import cancel_service, extend_service, refund, create_chat_id, db_manager, request_manager, chat_manager, function_descriptions_multiple, history
from config import users, secret_key, my_api_key, model_name



openai.api_key = my_api_key
memory_length = 20

app = Flask(__name__)
app.secret_key = secret_key
authenticate = Authentication().authenticate

llm = ChatOpenAI(model = model_name, temperature = 0, openai_api_key = my_api_key)






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

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')

    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
        
        global history
        if len(history) == 0:
            chat_id = create_chat_id()
        else:
            chat_id = history[0]['chat_id']

        user_prompt_ = request.form['user_message']

        system_message = f"""You are a Customer Service Bot. Consider your own conversation history in chat:
            history: {history}
            """

        first_response = llm.predict_messages(
        [HumanMessage(content = user_prompt_),
        SystemMessage(content = system_message)],

        functions = function_descriptions_multiple,
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
        
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
