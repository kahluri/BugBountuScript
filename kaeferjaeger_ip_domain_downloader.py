import requests
import os
import sys
from tqdm import tqdm
import re
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# List of URLs and corresponding filenames with color codes
download_list = [
    ('https://kaeferjaeger.gay/sni-ip-ranges/oracle/ipv4_merged_sni.txt', 'oracle_ipv4_merged_sni.txt', Fore.RED),
    ('https://kaeferjaeger.gay/sni-ip-ranges/amazon/ipv4_merged_sni.txt', 'amazon_ipv4_merged_sni.txt', Fore.GREEN),
    ('https://kaeferjaeger.gay/sni-ip-ranges/digitalocean/ipv4_merged_sni.txt', 'digitalocean_ipv4_merged_sni.txt', Fore.BLUE),
    ('https://kaeferjaeger.gay/sni-ip-ranges/google/ipv4_merged_sni.txt', 'google_ipv4_merged_sni.txt', Fore.YELLOW),
    ('https://kaeferjaeger.gay/sni-ip-ranges/microsoft/ipv4_merged_sni.txt', 'microsoft_ipv4_merged_sni.txt', Fore.MAGENTA),
    ('https://kaeferjaeger.gay/sni-ip-ranges/oracle/ipv4_merged_sni.txt', 'oracle2_ipv4_merged_sni.txt', Fore.CYAN)
]

# Create a directory to store downloaded files
os.makedirs('downloads', exist_ok=True)

def download_file(url, filename, color):
    """
    Download a file with colorful progress bar
    
    Args:
        url (str): URL of the file to download
        filename (str): Name to save the file as
        color (str): Colorama color to use for progress bar
    
    Returns:
        str: Path to the downloaded file
    """
    # Full path for the file
    full_path = os.path.join('downloads', filename)
    
    # Send a GET request
    response = requests.get(url, stream=True)
    
    # Get the total file size
    total_size = int(response.headers.get('content-length', 0))
    
    # Open local file to write downloaded content
    with open(full_path, 'wb') as file:
        # Custom progress bar with color
        with tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            desc=f"{color}Downloading {filename}{Style.RESET_ALL}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        ) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress_bar.update(size)
    
    return full_path

def extract_domains_from_files(directory):
    """
    Extract unique domains from all .txt files in a directory
    
    Args:
        directory (str): Directory containing txt files
    
    Returns:
        set: Unique domains extracted
    """
    all_domains = set()
    
    # Iterate through all .txt files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    for line in file:
                        # Use regex to extract domains in square brackets
                        match = re.search(r'\[(.*?)\]', line)
                        if match:
                            # Split the matched domains, strip whitespace, remove duplicates
                            line_domains = [d.strip() for d in match.group(1).split()]
                            
                            # Add non-empty domains
                            all_domains.update(domain for domain in line_domains if domain)
            
            except Exception as e:
                print(f"{Fore.RED}Error processing file {filename}: {e}{Style.RESET_ALL}")
    
    return all_domains

def main():
    """
    Main function to download files and extract domains
    """
    # Print cool start message
    print(f"{Fore.CYAN}🚀 Starting Domain IP Range Downloader 🌐{Style.RESET_ALL}")
    
    # Download each file
    for url, filename, color in download_list:
        try:
            # Download the file with a unique name and color
            download_file(url, filename, color)
        except Exception as e:
            print(f"{Fore.RED}Error downloading {url}: {e}{Style.RESET_ALL}")
    
    # Extract domains from downloaded files
    print(f"\n{Fore.YELLOW}🔍 Extracting Unique Domains...{Style.RESET_ALL}")
    unique_domains = extract_domains_from_files('downloads')
    
    # Write unique domains to file
    with open('domainNames.txt', 'w', encoding='utf-8') as outfile:
        for domain in sorted(unique_domains):
            outfile.write(f"{domain}\n")
    
    # Print completion message
    print(f"\n{Fore.GREEN}✅ Download and Extraction Complete!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Total unique domains extracted: {len(unique_domains)}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Domains have been saved to domainNames.txt{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
