from .deadline import Deadline  # Relative import within the same directory
from .hollywoodreporter import HollywoodReporter  # Relative import within the same directory
from .screenrant import ScreenRant  # Relative import within the same directory
from .slashfilm import SlashFilm  # Relative import within the same directory
# from some_module import AnotherSource

class Engine:
    def __init__(self):
        # List of source classes to be processed with their corresponding URLs
        self.sources = [
            # {"class": Deadline, "enabled": True, "url": "https://deadline.com/v/film/"},
            # Add other sources here, e.g.:
            # {"class": HollywoodReporter, "enabled": True, "url": "https://www.hollywoodreporter.com/c/movies/"},
            # {"class": ScreenRant, "enabled": True, "url": "https://screenrant.com/movie-news/"},
            # {"class": AnotherSource, "enabled": False, "url": "https://example.com/another"},
            # {"class": Slashfilm, "enabled": True, "url": "https://www.slashfilm.com/category/movies/"},

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
