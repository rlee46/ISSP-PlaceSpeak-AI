def test_sentiment(data):
    sentiments = ['positive', 'neutral', 'negative']
    for entry in data:
        if not str(entry['Sentiment']).lower() in sentiments:
            print('sentiment')
            return False
        
    return True