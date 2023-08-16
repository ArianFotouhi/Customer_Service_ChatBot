import sqlite3

conn = sqlite3.connect('conversation.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id INTEGER PRIMARY KEY,
        user_message TEXT,
        bot_response TEXT,
        sentiment_fl FLOAT,
        sentiment_str TEXTT
    )
''')

for user_msg, bot_resp in chat_session:
    cursor.execute('INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)', (user_msg, bot_resp))
    conn.commit()

# Fetch and print the saved chat history
cursor.execute('SELECT user_message, bot_response FROM chat_history')
history = cursor.fetchall()

for row in history:
    user_msg, bot_resp = row
    print(f"{user_msg}\n{bot_resp}\n")

# Close the database connection
conn.close()
