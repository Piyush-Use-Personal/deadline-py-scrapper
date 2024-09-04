from .deadline import Deadline  # Relative import within the same directory
from .variety import Variety  # Relative import within the same directory
# from some_module import AnotherSource

class Engine:
    def __init__(self):
        # List of source classes to be processed with their corresponding URLs
        self.sources = [
            # {"class": Deadline, "enabled": True, "url": "https://deadline.com/v/film/"},
            {"class": Variety, "enabled": True, "url": "https://variety.com/v/film/"},
            # Add other sources here, e.g.:
            # {"class": AnotherSource, "enabled": False, "url": "https://example.com/another"},
        ]

    def run(self):
        all_results = []
        for source_info in self.sources:
            if source_info["enabled"]:
                source = source_info["class"]()
                url = source_info["url"]
                results = source.process(url)
                all_results.extend(results)
        return all_results
