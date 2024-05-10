class TestFunctions:
    def test_confidence(self, entries):
        try:
            return all(0 <= int(entry['ConfidenceScore'].rstrip('%')) <= 100 for entry in entries)
        except ValueError:
            return False

    def test_sentiment(self, entries):
        valid_sentiments = {'Positive', 'Neutral', 'Negative'}
        return all(entry['Sentiment'] in valid_sentiments for entry in entries)

    def validate_entries(self, entries):
        return self.test_confidence(entries) and self.test_sentiment(entries)