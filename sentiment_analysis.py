import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')  
sia = SentimentIntensityAnalyzer()

def analyzer(texts):
    sent_list = []
    for text in texts:

        sentiment_scores = sia.polarity_scores(text)
        sent_list.append(sentiment_scores)

    
    sent_agg = 0
    for i in sent_list:
        sent_agg = sent_agg +i['compound'] 
    
    sent_avg = sent_agg/len(sent_list)

    sentiment = "positive" if sent_avg > 0 else "negative" if sent_avg < 0 else "neutral"

    return sentiment, sent_avg

