import csv
import io

class CSVHandler:
    @staticmethod
    def download(data):
        output = io.StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=["title", "content", "author"])
        
        # Write header
        csv_writer.writeheader()
        
        # Write rows
        for item in data:
            csv_writer.writerow({
                "title": item["title"],
                "content": "\n".join(item["content"]),  # Join content list into a single string
                "author": item["author"]
            })
        
        # Reset pointer to start of StringIO buffer
        output.seek(0)
        
        return output.getvalue()
