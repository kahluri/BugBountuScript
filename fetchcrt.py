import requests
import argparse
import sys

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored_help():
    help_message = f"""
{Colors.HEADER}{Colors.BOLD}Usage:{Colors.ENDC}
  python fetchcrt.py [-h] -q QUERY [-f {{json,csv}}] [-d] [-e]

{Colors.HEADER}{Colors.BOLD}Description:{Colors.ENDC}
  Fetch and process certificate data from crt.sh

{Colors.OKGREEN}{Colors.BOLD}Options:{Colors.ENDC}
  -h, --help            Show this help message and exit.
  -q QUERY, --query QUERY
                        Specify the company or subdomain you want to extract data for (e.g., google).
  -f {{json,csv}}, --format {{json,csv}}
                        Specify the format of the data to download ('json' or 'csv'). Use this option with -d.
  -d, --download        Download the data in the specified format (use with -f).
  -e, --extract         Extract `common_name` and `name_value` from the data and store them in 'fetchcrtSubDomain_<query>.txt'.
                        It also downloads both JSON and CSV files.

{Colors.OKBLUE}{Colors.BOLD}Examples:{Colors.ENDC}
  1. Download a JSON file:
     {Colors.OKCYAN}python fetchcrt.py -q google -f json -d{Colors.ENDC}

  2. Download a CSV file:
     {Colors.OKCYAN}python fetchcrt.py -q google -f csv -d{Colors.ENDC}

  3. Extract specific fields (`common_name` and `name_value`) and save to 'fetchcrtSubDomain_google.txt':
     {Colors.OKCYAN}python fetchcrt.py -q google -e{Colors.ENDC}
"""
    print(help_message)

def download_file(query, file_format, save_as=None):
    base_url = "https://crt.sh"
    url = f"{base_url}/{file_format}?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        file_extension = "json" if file_format == "json" else "csv"
        filename = save_as or f"fetchcrt__{query}.{file_extension}"
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"{Colors.OKGREEN}File downloaded successfully: {filename}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Failed to download file. HTTP Status Code: {response.status_code}{Colors.ENDC}")

def extract_data(query):
    url = "https://crt.sh/json"
    params = {"q": query}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        # Save extracted subdomain data
        subdomain_filename = f"fetchcrtSubDomain_{query}.txt"
        with open(subdomain_filename, "w") as subdomain_file:
            data = response.json()
            for item in data:
                common_name = item.get("common_name", "")
                name_value = item.get("name_value", "")
                subdomain_file.write(f"{common_name}\n{name_value}\n")
        print(f"{Colors.OKGREEN}Data extracted and saved to {subdomain_filename}.{Colors.ENDC}")
        
        # Save JSON and CSV files as part of extraction
        download_file(query, "json", save_as=f"fetchcrt__{query}.json")
        download_file(query, "csv", save_as=f"fetchcrt__{query}.csv")
    else:
        print(f"{Colors.FAIL}Failed to extract data. HTTP Status Code: {response.status_code}{Colors.ENDC}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and process certificate data from crt.sh",
        add_help=False
    )
    parser.add_argument("-q", "--query", help="Specify the company or subdomain you want to extract data for (e.g., google).")
    parser.add_argument("-f", "--format", choices=["json", "csv"], help="Specify the format of the data to download ('json' or 'csv'). Use this option with -d.")
    parser.add_argument("-d", "--download", action="store_true", help="Download the data in the specified format (use with -f).")
    parser.add_argument("-e", "--extract", action="store_true", help="Extract `common_name` and `name_value` and save to 'fetchcrtSubDomain_<query>.txt'.")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.help:
        print_colored_help()
    elif args.query:
        if args.download:
            if not args.format:
                print(f"{Colors.FAIL}Error: Please specify the file format (-f json or -f csv) for downloading.{Colors.ENDC}")
            else:
                download_file(args.query, args.format)
        elif args.extract:
            extract_data(args.query)
        else:
            print(f"{Colors.FAIL}Error: Please specify either -d to download or -e to extract data.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Error: The query (-q) argument is required.{Colors.ENDC}")

