import requests
import sys

GITHUB_TOKEN = "github_pat"  # Add your GitHub token

def get_github_contents(repo_url):
    print("Starting to fetch GitHub repository contents...")
    parts = repo_url.rstrip('/').split('/')
    
    if len(parts) < 5 or parts[2] != "github.com":
        print("Error: Invalid GitHub URL. Please check the format.")
        raise ValueError("Invalid GitHub URL. Ensure the URL is in the format: https://github.com/user/repo/tree/branch/path")
    
    user = parts[3]
    repo = parts[4]
    
    if "tree" in parts:
        branch = parts[6]
        subpath = '/'.join(parts[7:]) if len(parts) > 7 else ''
        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{subpath}?ref={branch}"
    else:
        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/"
    
    print(f"Fetching contents from: {api_url}")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    print("Repository contents fetched successfully.")
    return response.json()

def process_contents(contents, paths=[], parent_path=""):
    print("Processing repository contents...")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    for item in contents:
        path = parent_path + item['name']
        print(f"Processing: {path}")
        
        if item['type'] == 'dir':
            print(f"Entering directory: {path}")
            dir_response = requests.get(item['url'], headers=headers)
            dir_response.raise_for_status()
            dir_contents = dir_response.json()
            process_contents(dir_contents, paths, path + "/")
        else:
            print(f"Fetching file content: {path}")
            file_response = requests.get(item['download_url'], headers=headers)
            file_response.raise_for_status()
            print(f"File content downloaded: {path}")
            file_content = file_response.text
            formatted_content = f"{path}\n------\n{file_content}\n------"
            paths.append(formatted_content)
    
    print(f"Finished processing. Total files processed: {len(paths)}.")
    return paths

def write_to_txt(data, output_file):
    print(f"Writing data to TXT file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as txtfile:
        txtfile.write('\n\n'.join(data))
    print(f"TXT file '{output_file}' written successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <repo_url> <output_txt_path>")
        sys.exit(1)

    repo_url = sys.argv[1]
    output_path = sys.argv[2]

    try:
        print(f"Starting script for repository: {repo_url}")
        contents = get_github_contents(repo_url)
        paths = process_contents(contents)
        write_to_txt(paths, output_path)
        print("Script executed successfully.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
    except FileNotFoundError as e:
        print(f"File Error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")