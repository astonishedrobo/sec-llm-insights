import os
from datetime import datetime
from sec_edgar_downloader import Downloader
import argparse

def download_10k_filings(company_name, email_address, ticker, start_year = None, end_year = None):
    # Create a directory to store the downloaded files
    data_dir = f"data"
    os.makedirs(data_dir, exist_ok=True)

    # Initialize the Downloader
    dl = Downloader(company_name, email_address, os.path.join(os.getcwd(), data_dir))

    # Convert start_year to a datetime object
    start_date = datetime(start_year, 1, 1)

    try:
        # Download the 10-K filings from the start_date until the end_year
        num_filings = dl.get("10-K", ticker, limit=None, after=start_date, before=datetime(end_year + 1, 1, 1) if end_year else None, include_amends=False, download_details=True)
        print(f"Downloaded {num_filings} 10-K filings for {ticker} from {start_year if start_year else 'the earliest available'} to {end_year if end_year else 'the latest available'}")

    except Exception as e:
        print(f"Error downloading or cleaning 10-K filings for {ticker}: {e}")

def main():
    args = parse_args()
    download_10k_filings(args.company, args.email, args.ticker, args.start_year, args.end_year)
    return 0

def parse_args():
    parser = argparse.ArgumentParser(description="Download 10-K filings for a company")
    parser.add_argument("--company", type=str, help="The company name")
    parser.add_argument("--email", type=str, help="The email address")
    parser.add_argument("--ticker", type=str, help="The company ticker")
    parser.add_argument("--start_year", type=int, default=None, help="The start year")
    parser.add_argument("--end_year", type=int, default=None, help="The end year")
    return parser.parse_args()

if __name__ == "__main__":
    main()
