import csv
import io

class CSVHandler:
    @staticmethod
    def download(data):
        output = io.StringIO()
        fieldnames = ["title", "content", "author_name", "date", "categories", "url", "banner", "author_url", "time", "category", "thumbnail"]
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Write header
        csv_writer.writeheader()
        
        # Write rows
        for item in data:
            csv_writer.writerow({
                "title": item.get("title", ""),
                "content": "\n".join(item.get("content", [])),  # Join content list into a single string
                "author_name": item.get("author_name", ""),
                "date": item.get("date", ""),
                "categories": ", ".join(item.get("categories", [])),  # Join categories list into a comma-separated string
                "url": item.get("url", ""),
                "banner": item.get("banner", ""),
                "author_url": item.get("author_url", ""),
                "time": item.get("time", ""),
                "category": item.get("category", ""),
                "thumbnail": item.get("thumbnail", "")
            })
        
        # Reset pointer to start of StringIO buffer
        output.seek(0)
        
        return output.getvalue()
