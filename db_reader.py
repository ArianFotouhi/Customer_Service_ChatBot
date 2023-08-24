from bot_db import ChatDatabase, RequestDatabase

db = ChatDatabase()
# db = RequestDatabase()

db.create_table()


#table_name = 'chat_history'
#query = f"PRAGMA table_info({table_name})"

output = db.fetch_table(query='''SELECT user_message, bot_response, datetime
FROM chat_history
ORDER BY datetime DESC
LIMIT 20;
''')
                        
history = []
for i in output:

    # print(i[0])
    history.append({'user': i[0], 'customer_service_bot': i[1], 'datetime': i[2]})

print(history)
