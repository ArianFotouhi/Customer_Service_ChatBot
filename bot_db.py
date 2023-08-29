import sqlite3

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('conversation.db')
        self.cursor = self.conn.cursor()

    def create_table(self):

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                chat_id TEXT NOT NULL,
                user_message TEXT,
                bot_response TEXT,
                datetime DATETIME,
                category TEXT,        
                sentiment_fl FLOAT,
                sentiment_str TEXT
            )
        ''')
    def commit_table(self, chat_id, user_message, bot_response, datetime, category, sentiment_fl, sentiment_str):
        self.cursor.execute('INSERT INTO chat_history (chat_id, user_message, bot_response, datetime, category, sentiment_fl, sentiment_str) VALUES (?,?, ?,?, ?,?, ?)', 
        (chat_id, user_message, bot_response, datetime, category, sentiment_fl, sentiment_str))
        
        self.conn.commit()

    def fetch_table(self, query = 'SELECT * FROM chat_history'):
        # Fetch and print the saved chat history
        self.cursor.execute(query)
        history = self.cursor.fetchall()

        # for row in history:
        #     print(row)
        # Close the database connection
        self.conn.close()
        return history


class RequestDatabase():
    def __init__(self):
        self.conn = sqlite3.connect('request.db')
        self.cursor = self.conn.cursor()

    def create_table(self):

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                chat_id TEXT NOT NULL,
                ref_num TEXT NOT NULL,
                booking_dt TEXT,
                reservation_dt TEXT,
                life_mile_cert TEXT,
                lounge_name TEXT,        
                new_dt DATETIME,
                additional_note TEXT,        
                first_name TEXT,
                last_name TEXT,
                email_addr TEXT,        
                req_sub_datetime TEXT,
                request_type TEXT
            )
        ''')
    def commit_table(self, chat_id, ref_num, booking_dt, reservation_dt, life_mile_cert, lounge_name, new_dt, additional_note, first_name, last_name, email_addr, req_sub_datetime, request_type):
        self.cursor.execute('INSERT INTO requests (chat_id, ref_num, booking_dt, reservation_dt, life_mile_cert, lounge_name, new_dt, additional_note, first_name, last_name, email_addr, req_sub_datetime, request_type) VALUES (?,?,?, ?,?, ?,?, ?,?,?, ?,?, ?)', 
        (chat_id, ref_num, booking_dt, reservation_dt, life_mile_cert, lounge_name, new_dt, additional_note, first_name, last_name, email_addr, req_sub_datetime, request_type)
        )
        
        self.conn.commit()

    def fetch_table(self, query = 'SELECT * FROM requests'):
        # Fetch and print the saved chat history
        self.cursor.execute(query)
        history = self.cursor.fetchall()

        for row in history:
            print(row)
        # Close the database connection
        self.conn.close()
