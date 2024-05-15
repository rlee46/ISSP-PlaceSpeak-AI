import re
import csv
from io import StringIO

class HelperFunctions:
    def count_csv_rows(self, csv_data):
        lines = csv_data.strip().split('\n')
        return len([line for line in lines if len(line) > 0])

    def csv_to_array(self, csv_data):
        try:
            data = []
            reader = csv.DictReader(StringIO(csv_data))
            skip_first_row = True
            for row in reader:
                if skip_first_row:
                    skip_first_row = False
                    continue
                data.append(row)
            return data
        except Exception as e:
            return e

    def remove_non_printable_chars(self, text):
        printable_pattern = re.compile(r'[^\x20-\x7E]')
        return re.sub(printable_pattern, '', text)

    def num_tokens(self, data):
        pattern = r'\w+|[^\w\s]'
        tokens = re.findall(pattern, data)
        return len(tokens)    