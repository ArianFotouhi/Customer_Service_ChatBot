import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('conversation.db')
        self.cursor = self.conn.cursor()

    def create_table(self):

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                datetime DATETIME,
                user_message TEXT,
                bot_response TEXT,
                sentiment_fl FLOAT,
                sentiment_str TEXT
                                       
            )
        ''')
    def commit_table(self, chat_id, datetime, user_message, bot_response, sentiment_fl, sentiment_str):
        self.cursor.execute('INSERT INTO chat_history (chat_id, datetime, user_message, bot_response, sentiment_fl, sentiment_str) VALUES (?,?, ?,?, ?,?)', ( chat_id, datetime, user_message, bot_response, sentiment_fl, sentiment_str))
        self.conn.commit()

    def fetch_table(self, query = 'SELECT * FROM chat_history'):
        # Fetch and print the saved chat history
        self.cursor.execute(query)
        history = self.cursor.fetchall()

        for row in history:
            print(row)
        # Close the database connection
        self.conn.close()
