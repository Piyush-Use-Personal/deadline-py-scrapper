import csv
import io

class CSVHandler:
    @staticmethod
    def download(data):
        output = io.StringIO()
        fieldnames = [
            "title", "content", "author", "published_date", "published_time",
            "url_article", "url_banner_image", "url_thumbnail_image",
            "captured_date", "captured_time", "source", "source_icon_url", "source_section"
        ]
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Write header
        csv_writer.writeheader()
        
        # Write rows
        for item in data:
            csv_writer.writerow({
                "title": item.get("title", ""),
                "content": "\n".join(item.get("content", [])),  # Join content list into a single string
                "author": item.get("author", ""),
                "published_date": item.get("publishedDate", ""),
                "published_time": item.get("publishedTime", ""),
                "url_article": item.get("urlArticle", ""),
                "url_banner_image": item.get("urlBannerImage", ""),
                "url_thumbnail_image": item.get("urlThumbnailImage", ""),
                "captured_date": item.get("capturedDate", ""),
                "captured_time": item.get("capturedTime", ""),
                "source": item.get("source", ""),
                "source_icon_url": item.get("sourceIconURL", ""),
                "source_section": item.get("sourceSection", "")
            })
        
        # Reset pointer to start of StringIO buffer
        output.seek(0)
        
        return output.getvalue()
