def test_confidence(data):
    for entry in data:
        try:
            a = int((entry['ConfidenceScore'].replace('%-', '')))
        except:
            print('type error')
            return False
        
        if not(a >=0 or a <= 100):
            print('bad value')
            return False
        
    return True
        
