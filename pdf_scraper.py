""" Scrape PDF files from Google by a search query. """
import os
from os.path import abspath, dirname, join
from threading import Thread
import urllib.request
import requests
from bs4 import BeautifulSoup

# Variables.
urls = []


def create_results_folder(folder_name: str = "pdf_results"):
    """Create a folder to store results.
    Keyword arguments:
        folder_name (str): Destination folder name. (default: "pdf_results")
    Returns:
        str. The full folder path of downloads.
    """
    folder_full_path = join(dirname(abspath(__file__)), folder_name)
    # Create folder.
    if not os.path.exists(folder_full_path):
        os.makedirs(folder_full_path)
    return folder_full_path


def download_file(d_url: str, folder_full_path: str):
    """Download a file from a URL.
    Keyword arguments:
        d_url (str): Download URL for the file.
        folder_full_path (str): Full path of downloads folder..
    """

    # Extract file name.
    filename = d_url.split('/')[-1].replace(" ", "_")
    file_path = join(folder_full_path, filename)

    # Download request.
    d_req = requests.get(d_url, stream=True)
    if d_req.ok:
        print("Saving to: ", os.path.abspath(file_path))
        # Save file.
        with open(file_path, "wb") as d_file:
            for chunk in d_req.iter_content(chunk_size=1024 * 8):
                if chunk:
                    d_file.write(chunk)
                    d_file.flush()
                    os.fsync(d_file.fileno())
    else:  # HTTP status code 4XX/5XX
        with open(join(folder_full_path, "errors.txt"), "a", encoding="utf-8") as log_file:
            log_file.write(
                f"Download failed: status code {d_req.status_code}\n{d_req.text}\n\n")


def get_pdfs(query: str, page: int = 1):
    """Scrape PDFs URLs from Google.
    Keyword arguments:
        query (str): Search query.
    """
    text = urllib.parse.quote_plus(query)
    # Add "&gl=us&hl=en" for English only results.
    pdf_url = f"https://google.com/search?q={text}:pdf&start={str((page-1)* 10)}"
    response = requests.get(pdf_url)

    # Loop through results.
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.findAll("a"):
        href = link["href"]
        if ".pdf" in href:
            # Parse href.
            href = href.replace("/url?q=", "").split(".pdf", 1)[0] + ".pdf"
            urls.append(href)


# Get pdfs and download each one.
start_page = int(input("Start page: "))
end_page = int(input("End page: "))

# Create downloads folder.
folder_path = create_results_folder()

# Loop through pages.
print("\n----------Scraping Results:----------")
for current in range(start_page, end_page+1):
    print(f"\nScraping from page: {current}")
    get_pdfs("cours info", current)


# Download from each url.
print("\n----------Download Results:----------")
for url in urls:
    download_file(url, folder_path)
    new_thread = Thread(target=download_file, args=(url, folder_path))
    new_thread.start()
