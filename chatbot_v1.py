import json
import openai
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

my_openai_key = ""
openai.api_key = my_openai_key
memory_length = 20
history = []


def cancel_service():
    ans = input('please say yes if you are sure to cancel your service? ')
    
    if ans.lower() == 'yes':
        pass
    else:
        return 'The request is not created for cancelation'

    return 'Based on the received account detail the request is submitted, please email to cancel@company.com as the final step. Have a nice day!'

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



llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0, openai_api_key = my_openai_key)


while True:
    system_message = f"""You are a Customer Service Bot. Consider the conversation history in chat:
    history: {history}
    """
    print('history', system_message)

    user_prompt_ = input('ask me: ')

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
        
        print('func out', func_output)
        second_response = llm.predict_messages(
        [
            HumanMessage(content=user_prompt_),
            AIMessage(content=str(first_response.additional_kwargs)),
            AIMessage(
                role="function",
                additional_kwargs={
                    "name": first_response.additional_kwargs["function_call"]["name"]
                },
                content= func_output,
            ),
        ],
            functions=function_descriptions_multiple,
        )
        history.insert(0, {'Human user': user_prompt_, 
        'Customer bot': func_output,
          'time':datetime.now()})

#        print('second_resp', second_response.content)
    
    except:
        history.insert(0, {'Human user': user_prompt_, 
          'Customer bot': first_response.content, 'time':datetime.now()})
#        print(first_response.content)
