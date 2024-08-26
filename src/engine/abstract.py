from abc import ABC, abstractmethod

class AbstractSource(ABC):
    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def getPrimaryContent(self):
        pass

    @abstractmethod
    def getChildLinks(self):
        pass

    @abstractmethod
    def processChildren(self):
        pass

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
