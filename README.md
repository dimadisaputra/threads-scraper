
# Threads Post Reply Scraper (GraphQL Request)

This project is a Python-based scraper for fetching and saving replies to posts on Threads, a text-based social platform by Instagram.

## Features

- Fetch replies to a specific Threads post
- Save data in multiple formats (JSON, CSV, XLSX)
- Paginate through all replies
- Extract detailed information about each reply, including user data and engagement metrics

## Requirements

- Python 3.7+
- Required Python packages (install via `pip install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - pandas
  - python-dotenv
  - jsonpath-ng

## Setup

1. Clone this repository:
```sh
git clone https://github.com/dimadisaputra/threads-scraper.git
```
```sh
cd threads-reply-scraper
```
2. Install the required packages:
```sh
pip install -r requirements.txt
```
3. Create a `.env` file in the project root and add your Threads cookie:
```sh
COOKIE=your_threads_cookie_here
```

## Usage

Run the script from the command line:
```sh
python main.py --url <threads_post_url> --format <output_format> --output_dir <output_directory>
```

Arguments:
- `--url`: URL of the Threads post (required)
- `--format`: Output file format. Options: json, csv, xlsx (default: json)
- `--output_dir`: Directory to save the output file (default: data)

Example:
```sh
python main.py --url "https://www.threads.net/@username/post/ABC123" --format csv --output_dir output
```
