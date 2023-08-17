import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')  
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(texts):
    sent_list = []
    for text in texts:

        sentiment_scores = sia.polarity_scores(text)
        sent_list.append(sentiment_scores)

    print('senti_list', sent_list)
    
    sent_agg = 0
    for i in sent_list:
        sent_agg = sent_agg +i['compound'] 
    
    sent_avg = sent_agg/len(sent_list)
    print('final result', sent_avg)

    sentiment = "positive" if sent_avg > 0.15 else "negative" if sent_avg < -0.15 else "neutral"

    return sentiment, sent_avg


