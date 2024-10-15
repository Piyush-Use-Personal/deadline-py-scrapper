from .deadline import Deadline  # Relative import within the same directory
from .hollywoodreporter import (
    HollywoodReporter,
)  # Relative import within the same directory
from .screenrant import ScreenRant  # Relative import within the same directory
from .slashfilm import SlashFilm  # Relative import within the same directory
from .screenDaily import ScreenDaily  # Relative import within the same directory
from .variety import Variety  # Relative import within the same directory
from .atlantic import Atlantic  # Relative import within the same directory
from .nyTimes import NyTimes
from .collider import Collider
from .indiewire import IndieWire

# from some_module import AnotherSource


class Engine:
    def __init__(self):
        # List of source classes to be processed with their corresponding URLs
        self.sources = [
            # {"class": Deadline, "enabled": True, "url": "https://deadline.com/v/film/"},
            # {"class": Variety, "enabled": True, "url": "https://variety.com/v/film/"},
            # Add other sources here, e.g.:
            # {"class": HollywoodReporter, "enabled": True, "url": "https://www.hollywoodreporter.com/c/movies/"},
            # {"class": ScreenRant, "enabled": True, "url": "https://screenrant.com/movie-news/"},
            # {"class": SlashFilm, "enabled": True, "url": "https://www.slashfilm.com/category/movies/"},
            # {"class": Atlantic, "enabled": True, "url": "https://www.theatlantic.com/culture/"},
            # {
            #     "class": NyTimes,
            #     "enabled": True,
            #     "url": "https://www.nytimes.com/section/movies",
            # },
            {
                "class": IndieWire,
                "enabled": True,
                "url": "https://www.indiewire.com/c/criticism/movies/",
            },
            # {"class": Collider, "enabled": True, "url": "https://collider.com/"},
            # {"class": ScreenDaily, "enabled": True, "url": "https://www.screendaily.com/box-office"},
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
