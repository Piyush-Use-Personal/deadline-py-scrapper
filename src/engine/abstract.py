from typing import Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import pytz

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
    def to_json(self):
        pass

    def extract_date_time_from_iso(self, iso_string: str):
        
        """
        Extracts date and time from an ISO 8601 string.

        :param iso_string: The ISO 8601 date-time string
        :return: A tuple containing the date and time
        """
        if iso_string:
            # Parse the ISO string
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            
            # Format date and time
            date = dt.date().isoformat()  # 'YYYY-MM-DD'
            time = dt.time().isoformat()  # 'HH:MM:SS'

            return date, time
        return "", ""
    
    def extract_date_time(self, date_str):
        # Define the format of the input string
        date_format = "%B %d, %Y %I:%M%p"
        
        # Convert the input string to a datetime object
        dt = datetime.strptime(date_str, date_format)
        
        # Format the extracted date and time
        extracted_date = dt.strftime("%Y-%m-%d")
        extracted_time = dt.strftime("%H:%M:%S")
    
        return extracted_date, extracted_time

    def parse_datetime(self, date_str: str) -> Optional[Tuple[datetime, datetime]]:
        def parse_date(date_string:str):
            formats = ["%B %d, %Y %I:%M%p", "%b %d, %Y %I:%M%p"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            return "Invalid date format"
        
        if date_str: 
            # Remove the timezone abbreviation (PT) for parsing
            date_str = date_str.replace("PT", "").strip()
            
            # Parse the string into a naive datetime object
            dt_naive =  parse_date(date_str)
            
            # Define timezone (Pacific Time)
            pacific_tz = pytz.timezone('America/Los_Angeles')
            
            # Localize the naive datetime object to Pacific Time
            dt_pacific = pacific_tz.localize(dt_naive)
            
            # Extract date and time separately
            date_only = dt_pacific.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
            time_only = dt_pacific.strftime("%I:%M %p")   # Format as HH:MM AM/PM
            
            return date_only, time_only
        return "", ""
        
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
