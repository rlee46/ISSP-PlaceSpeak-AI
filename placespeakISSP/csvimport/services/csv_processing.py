from django.http import JsonResponse
import os
import json
import requests
import math
import time
import csv
from collections import defaultdict
from rest_framework.response import Response
from multiprocessing.pool import ThreadPool

from ..utilities.helpers import HelperFunctions
from ..tests.test_functions import TestFunctions
from ..serializer import AnalysisDataSerializer

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer {api_key}".format(api_key=self.api_key),
            "Content-Type": "application/json"
        }
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")

    def generate_completion(self, query):
        query_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            "max_tokens": 4096
        }
        response = requests.post(self.api_url, headers=self.headers, json=query_data)
        return response

class DataProcessorFactory:
    def __init__(self):
        self.helper = HelperFunctions()
        self.openai_client = OpenAIClient()
        self.test = TestFunctions()

    def get_processor(self, data_type):
        if data_type == "discussion":
            return DiscussionDataProcessor(self.openai_client, self.helper, self.test)
        elif data_type == "survey":
            return SurveyDataProcessor(self.openai_client, self.helper, self.test)
        else:
            raise ValueError("Unsupported data type: {data_type}")

class DiscussionDataProcessor:
    def __init__(self, openai_client, helper, tester):
        self.openai_client = openai_client
        self.helper = helper
        self.tester = tester

    def process_batch(self, batch_data):
        valid_result = False
        result = ""
        resultCount = 0
        row_count = len(batch_data)
        batch_data_str = str(batch_data)

        while not valid_result:
            # Construct the query
            query = """
            Generate the result in csv format without any explanation. Do not include a header for the data. For each response,
            column 1: Select one or more keywords from the response. If there is more than one keyword, separate them with `&` not commas
            column 2: Evaluate the sentiment of the response from positive, neutral, or negative
            column 3: Determine the reaction/emotion
            column 4: Generate a confidence score in a percentage
            column 5: Determine the location of the response from csv data
            Format the data as Key Words, Sentiment, Reaction/Emotion, Confidence Score, Location
            Here is an example: `Freedom & Responsibility, Positive, Happy, 100%, City of Burnaby`
            Note: The last number is the rows. Return the same number of rows in response
            """ + batch_data_str + " ROWS: " + str(row_count)  # Concatenate batch_data_str
            response = self.openai_client.generate_completion(query).json()

            if response['choices']:
                result = response['choices'][0]['message']['content']
                resultCount = self.helper.count_csv_rows(result)

                if resultCount == row_count:
                    # Parse result and validate entries
                    batch_entries = []
                    for line in result.strip().split("\n"):
                        parts = line.split(',')
                        try:
                            entry = {
                                'KeyPhrases': parts[0].strip(),
                                'Sentiment': parts[1].strip(),
                                'ReactionEmotion': parts[2].strip(),
                                'ConfidenceScore': parts[3].strip(),
                                'Location': parts[4].strip()
                            }
                            batch_entries.append(entry)
                        except IndexError:
                            continue

                    if self.tester.test_confidence(batch_entries) and self.tester.test_sentiment(batch_entries):
                        valid_result = True  # Validated successfully
                    else:
                        print("Validation failed, rerunning...")
                        time.sleep(5)  # Short delay before retry
                else:
                    print("Incorrect number of rows, rerunning...")
            else:
                print("API call failed or returned no choices, rerunning...")
                time.sleep(5)  # Short delay before retry

        return result

    def generate_analysis(self, csv_data):
        summary_data = self.summary_prompt(csv_data)
        table_data = self.table_prompt(csv_data)

        confidence_frequencies = self.calculate_frequencies(table_data)
        sentiment_frequencies = self.calculate_sentiment_frequencies(table_data)

        analysis_data = {
            "summary": summary_data,
            "entries": table_data,
            "confidence_frequencies": confidence_frequencies,
            "sentiment_frequencies": sentiment_frequencies
        }

        serializer = AnalysisDataSerializer(data=analysis_data)
        if serializer.is_valid():
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)
    
    def calculate_sentiment_frequencies(self,entries):
        sentiment_counts = defaultdict(int)
        for entry in entries:
            sentiment = entry.get('Sentiment', '').capitalize()
            if sentiment in ['Neutral', 'Positive', 'Negative']:
                sentiment_counts[sentiment] += 1
        return dict(sentiment_counts)

    def calculate_frequencies(self, entries):
        # Convert confidence scores to integers and bin them
        bins = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']
        score_bins = {bin: 0 for bin in bins}
    
        for entry in entries:
            score = int(entry['ConfidenceScore'].rstrip('%'))
            bin_index = min(score // 10, 9)  # to put 100% in the '90-100' bin
            bin_label = bins[bin_index]
            score_bins[bin_label] += 1

        return [score_bins[bin] for bin in bins]
    


#     def prompt(self, query_type, data):
    
#         # Prepare data to send to the OpenAI API
#         if query_type == 'summary':
#             query = '''
#             I am a government  official who is looking to make a decision based on the input of my community. 
#             The following data is sourced from a discussion post where members of my community discussed their views on the topic.
#             Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
#             In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
#             Do not format it in markdown, only use plain text.
#             ''' + data
        
#             return self.openai_client.generate_completion(query)
#         elif query_type == 'table':
#             start_time = time.time()
#             count = 0
#             batch_number = 0
#             token_limit = 3000
#             data_array = self.helper.csv_to_array(data)
#             print("array made")
#             batch_size = 5
#             results = []
#             current_batch = []
#             num_rows = len(data_array)
#             num_batches = math.ceil(num_rows / batch_size)
#             print("number of batches: " + str(num_batches))
        
#             results = []

#             for row in data_array:
#         # Calculate the number of tokens in the current row
#                 row_tokens = self.helper.num_tokens(str(row))
#         # Check if adding this row exceeds the token limit
#                 if count + row_tokens <= token_limit:
#                     current_batch.append(row)
#                     count += row_tokens
#                 else:
#             # Process the current batch
#                     print("--------------------------------------------------------")
#                     print("Batch Number: " + str(batch_number))
#                     batch_number += 1
#                     print("Num Tokens: " + str(count))
#                     print("Num of input rows: " + str(len(current_batch)))
#                     batch_result = self.process_batch(current_batch)
#                     print("--------------------------------------------------------")
#                     results.append(batch_result)
        
#         # Reset count and current batch
#                     count = row_tokens
#                     current_batch = [row]

# # Process the remaining batch if any
#             if current_batch:
#                 print("--------------------------------------------------------")
#                 print("Batch Number: " + str(batch_number))
#                 batch_number += 1
#                 print("Num Tokens: " + str(count))
#                 print("Num of input rows: " + str(len(current_batch)))
#                 batch_result = self.process_batch(current_batch)
#                 print("--------------------------------------------------------")
#                 results.append(batch_result)

#         end_time = time.time()  # End timing
#         print("Total processing time: {:.2f} seconds".format(end_time - start_time))
#         return results
    
    def prompt(self, query_type, data):
        if query_type == 'table':
            start_time = time.time()
            data_array = self.helper.csv_to_array(data)
            token_limit = 3000
            current_batch = []
            count = 0
            batches = []
            
            # Organize data into batches considering the token limit
            for row in data_array:
                row_tokens = self.helper.num_tokens(str(row))
                if count + row_tokens <= token_limit:
                    current_batch.append(row)
                    count += row_tokens
                else:
                    batches.append(current_batch)
                    current_batch = [row]
                    count = row_tokens
            if current_batch:
                batches.append(current_batch)
            
            results = []
            # Use ThreadPool to process batches concurrently
            pool = ThreadPool(processes=5)
            results = pool.map(self.process_batch, batches)
            pool.close()
            pool.join()
            end_time = time.time()  # End timing
            print("Total processing time: {:.2f} seconds".format(end_time - start_time))
            return results
        elif query_type == 'summary':
            query = '''
            I am a government  official who is looking to make a decision based on the input of my community. 
            The following data is sourced from a discussion post where members of my community discussed their views on the topic.
            Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
            In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
            Do not format it in markdown, only use plain text.
            ''' + data
        
            return self.openai_client.generate_completion(query)

    def summary_prompt(self, csv_data):
        response = self.prompt('summary', csv_data)
        if response.status_code == 200:
            summary_data = response.json()
            return summary_data.get("choices")[0].get("message").get("content")
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    def table_prompt(self, csv_data):
        # Loops the prompt untill the returned values pass the data tests
        entries = []
        result = self.prompt('table', csv_data)
        # Send the request to the OpenAI API
        
        for i in range(len(result)):
        
        # Parse the response data into an array of objects where each object is one row in the table
            
            for line in result[i].strip().split("\n"):
                parts = line.split(',')
                try:
                    entry = {
                        'KeyPhrases': parts[0].strip(),
                        'Sentiment': parts[1].strip(),
                        'ReactionEmotion': parts[2].strip(),
                        'ConfidenceScore': parts[3].strip(),
                        'Location': parts[4].strip()  # New column for location
                    }
                    
                    entries.append(entry)
                except:
                    break

            # Test data to see if resembles our expectations  
            # Test confidence scores ensures that the value associated with the confidence score attribute is an integer between 0 and 100
            # Test sentiment ensures that the value associated with the sentiment attribute is one of ['Positive', 'Neutral', 'Negative'] 
            # Should either of these tests fail, the prompt is rerun after a short delay 
        print(entries)
        print("table_prompt done")
            
        return entries
            

    def build_summary_prompt(self, data):
        return """
        I am a government official making a decision based on community input.
        Here is discussion post data about members' views.
        Provide a summary in 5-10 sentences and a 3-sentence recommendation.
        {data}
        """
    
#Survey Processing
#this class is used to process survey CSV files
#currently analyzes Binary/MCQ, Scale, and Text questions
class SurveyDataProcessor:
    def __init__(self, openai_client, helper, tester):
        self.openai_client = openai_client
        self.helper = helper
        self.tester = tester

    #Separate the questions in the CSV to analyze separately
    #NOTE columns_to_keep are the columns for questions.
    #Column 7 is the first question, '-2' means up to the second last column
    # Args:
    #   csv_data: dict containing all the csv data for the survey
    # Return:
    #   json string of the questions
    def separate_columns(self, csv_data):
        csv_string = csv_data.encode('utf-8')
        
        csv_reader = csv.DictReader(csv_string.splitlines())
        fieldnames = csv_reader.fieldnames
        if fieldnames is None:
            raise ValueError("Fieldnames could not be extracted from CSV data.")

        first_question_column = 7
        last_question_column = -2
        # Determine columns to keep (from 8 to the second last column)
        columns_to_keep = fieldnames[first_question_column:last_question_column]

        # Initialize a dictionary to store the JSON object
        json_object = {col: [] for col in columns_to_keep}

        # Process each row in the CSV
        for row in csv_reader:
            for col in columns_to_keep:
                json_object[col].append(row[col])
        return json.dumps(json_object, indent=2)
    
    # Process questions and combine results
    # Args:
    #   questions: json string of questions
    # Return:
    #   json string of the questions and analysis
    def process_questions(self, questions):
        data = json.loads(questions)
        keys = data.keys()
        result = {}

        for key in keys:
            cleaned_string = key.replace(u'\ufeff', '')
            value = data.get(key)
            cleaned_value = [v.replace(u'\ufeff', '') for v in value]
            analysis = self.analyze_question(cleaned_string, cleaned_value)
            print(analysis)
            json_result = json.loads(analysis)
            result.update(json_result)
        return result

    # Analyze the question using chatGPT
    # Args:
    #   key: question
    #   value: responses 
    # Return:
    #   json string of the questions and analysis      
    def analyze_question(self, key, value):
        prompt = ""
        q_type = self.determine_question_type(value)
        batch_size = 5
        if q_type == "MCQ":
            prompt = """ 
            assist me in analyzing these questions. I need you to count the number of occurrences of yes and no as responses. return to me the question,
            followed by the frequency of yes and no responses. The frequency must be as a proportion. For example the result for the question 'What time of day are you affected by this? [Evening]'.
            would be {"What time of day are you affected by this? [Evening]": "{"Yes": "5", "No":"5"}}. Only return me the result object with no other explanations, calculations or extra text.
            """
        elif q_type == "Scale":
            prompt = """ 
            assist me in alayzing these questions. The question is asking the user to rate something on a scale.
            I need you to count the frequency of each number on the scale from 1 to the maximum number you find in
            the responses. The frequency must be displayed as a proportion. For example, for the quesiton
            'on a scale of 1-5 how happy are you?' The response would be {"on a scale of 1-5 how happy are you?": 
            {"1": "10", "2": "30", "3": "20", "4": "0", "5": "20"}}. Ensure all numbers from lower to upper bound are returned.
            For example in the question provided the scale is from 1-5. You should return a proportion for all numbers from 1-5
            even if they are "0". Only return me the result object with no other text or explanation.
            """
        elif q_type == "Long Text":
            prompt = """ 
            assist me in analyzing these questions. The question is asking the user for a long response. I need you
            to summarize the responses in 1 sentence maximum. For example for the question 'leave a comment on how you feel'
            the response would be: {"leave a comment on how you feel": ["I feel happy", "I feel angry"]}. The number
            of summaries should equal the number of responses given. Ensure they match before returning the result. Only return me
            the result object with no other explanation or text.
            NOTE: DO NOT GIVE ME PROPORTION
            """
        print("creating batches")
        results = {}
        num_batches = int(math.ceil(len(value) / batch_size) + 1)
        print(value)
        key = key[3:]
        for i in range(num_batches):
            start_index = i * batch_size
            end_index = start_index + batch_size
            try:
                batch_value = value[start_index:end_index]
            except Exception as e:
                print("Error occurred while creating batch:", e)
                continue  # Skip this batch and proceed with the next one

            print("batch created")
            query = "For the question: " + str(key) + prompt + str(batch_value)
            try:
                analysis = self.openai_client.generate_completion(query).json().get("choices")[0].get("message").get("content")
                batch_result = json.loads(analysis)

                for k, v in batch_result.items():
                    try:
                        # Attempt to access the results dictionary with the key
                        if key in results:
                            if q_type in ["MCQ", "Scale"]:
                                for sub_k, sub_v in v.items():
                                    print(v, sub_k, sub_v)
                                    sub_v_int = int(sub_v)
                                    if sub_k in results[key]:
                                        results[key][sub_k] += sub_v_int
                                    else:
                                        results[key][sub_k] = sub_v_int
                            elif q_type == "Long Text":
                                results[key].extend(v)
                        else:
                            if q_type in ["MCQ", "Scale"]:
                                results[key] = {sub_k: int(sub_v) for sub_k, sub_v in v.items()}
                            elif q_type == "Long Text":
                                results[key] = v
                    except KeyError as e:
                        print("KeyError occurred while accessing results:", e)
                        continue  # Skip this key and proceed with the next one
            except Exception as e:
                print("Error during analysis:", e)
                continue  # Skip this batch and proceed with the next one

        return json.dumps(results)

        return str(analysis)

    # Determine the type of question being analyzed
    # Args:
    #   answers: responses that determine the question type
    # Return:
    #   string Scale, Long Text, MCQ or Uncertain 
    def determine_question_type(self,answers):
        mcq_count = 0
        long_text_count = 0
        scale_count = 0
        
        for answer in answers:
        # Check if the answer is a number
            if answer.isdigit():
                scale_count += 1
            elif len(answer) > 10:
                long_text_count += 1
            else:
                mcq_count += 1

        # If all answers are numeric, return "Scale"
        if scale_count == len(answers):
            return "Scale"
        elif long_text_count > 0:
            return "Long Text"
        elif mcq_count > 0:
            return "MCQ"
        else:
            return "Uncertain"