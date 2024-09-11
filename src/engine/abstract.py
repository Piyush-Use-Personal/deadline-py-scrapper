from abc import ABC, abstractmethod
from datetime import datetime

class AbstractSource(ABC):
    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def get_primary_content(self):
        pass

    @abstractmethod
    def process_children(self):
        pass

    @abstractmethod
    def to_jSON(self):
        pass

    def extract_date_time(self, date_str):
        # Define the format of the input string
        date_format = "%B %d, %Y %I:%M%p"
        
        # Convert the input string to a datetime object
        dt = datetime.strptime(date_str, date_format)
        
        # Format the extracted date and time
        extracted_date = dt.strftime("%Y-%m-%d")
        extracted_time = dt.strftime("%H:%M:%S")
    
        return extracted_date, extracted_time

    def get_current_date_and_time(self):
        now = datetime.now()
        captured_date = now.strftime("%Y-%m-%d")
        captured_time = now.strftime("%H:%M:%S")
        return captured_date, captured_time

    def merge_lists_by_key(self, list1, list2, key):
        # Create a dictionary to store merged objects by the common key
        merged_dict = {}

        # First, add all items from list1 to the dictionary
        for item in list1:
            merged_dict[item[key]] = item

        # Then, update the dictionary with items from list2, merging the data
        for item in list2:
            if item[key] in merged_dict:
                merged_dict[item[key]].update(item)
            else:
                merged_dict[item[key]] = item

        # Convert the dictionary back to a list
        merged_list = list(merged_dict.values())

        return merged_list
