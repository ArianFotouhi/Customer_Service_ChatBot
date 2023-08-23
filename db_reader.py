from bot_db import ChatDatabase, RequestDatabase

db = ChatDatabase()
#db = RequestDatabase()
db.create_table()


#table_name = 'chat_history'
#query = f"PRAGMA table_info({table_name})"

db.fetch_table()
