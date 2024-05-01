import csv
import requests
import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def extract_href(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            anchor_tag = soup.find('a', {'class': 'buttonColor'})
            if anchor_tag:
                return anchor_tag['href']
            else:
                return f"No anchor tag found with class 'buttonColor' on {url}"
        else:
            return f"Failed to fetch URL {url}: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def process_url(url):
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            return extract_href(url)
        except Exception as e:
            print(f"Failed to process URL {url}. Retrying ({retry_count + 1}/{max_retries})...")
            retry_count += 1
    return f"Failed to process URL {url} after {max_retries} retries"

def main(url_file, output_file, num_threads):
    with open(url_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(process_url, urls))

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Visited URL', 'Extracted Link'])
        for url, result in zip(urls, results):
            writer.writerow([url, result])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract href attribute from anchor tag on given URLs and save to CSV")
    parser.add_argument("-f", "--file", help="File containing list of URLs", required=True)
    parser.add_argument("-o", "--output", help="Output CSV file path", default="extracted_links.csv")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads to use (default: 5)", default=5)
    args = parser.parse_args()

    main(args.file, args.output, args.threads)
