import re

class HelperFunctions:
    def count_csv_rows(self, csv_data):
        lines = csv_data.strip().split('\n')
        return len([line for line in lines if len(line) > 0])

    def csv_to_array(self, csv_data):
        lines = csv_data.strip().split('\n')
        header = lines.pop(0).split(',')
        lines = lines[1:]
        data_array = []
        for line in lines:
            values = line.split(',')
            data_array.append({key: values[i].strip() for i, key in enumerate(header)})
        return data_array

    def remove_non_printable_chars(self, text):
        printable_pattern = re.compile(r'[^\x20-\x7E]')
        return re.sub(printable_pattern, '', text)

    def num_tokens(self, data):
        pattern = r'\w+|[^\w\s]'
        tokens = re.findall(pattern, data)
        return len(tokens)    