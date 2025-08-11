import requests
from dotenv import load_dotenv, set_key
import os
import json

# Teste commit 3
def get_token_myanimelist():
    # Load environment variables from .env file
    load_dotenv()

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

    TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"


    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    tokens = response.json()

    dotenv_path = '.env'
    set_key(dotenv_path, "REFRESH_TOKEN", tokens['refresh_token'])
    set_key(dotenv_path, "ACCESS_TOKEN", tokens['access_token'])

    return tokens['access_token']
    #print("Access Token:", tokens['access_token'])
    #print("Refresh Token:", tokens['refresh_token'])

def get_anime_info(anime_code, headers, params, file_path):
    url_base = f'https://api.myanimelist.net/v2/anime/{anime_code}'

    response = requests.get(url_base, headers=headers, params=params)
    result = response.json()

    os.makedirs(file_path, exist_ok=True) 
    if (response.status_code == 200):
        try:
            with open(f"{file_path}/{anime_code}_info.json", "w") as file:
                json.dump(result, file)
                print(f'File {anime_code}_info.json created!')
        except IOError as e:
            raise("Error on saving anime info")
    elif (response.status_code == 400):
        raise("Error 400")
    else:
        print(f'Anormal status {response.status_code}')

def get_my_anime_list_page(url, headers, page, user, file_path, params={}):
    response = requests.get(url, headers=headers, params=params)
    result = response.json()

    if response.status_code == 401:
        return url, page, response.status_code
    
    full_path = file_path + user
    os.makedirs(full_path, exist_ok=True) 
    if response.status_code == 200:
        try:
            with open(f"{full_path}/my_list_{page}.json", "w") as file:
                json.dump(result["data"], file)
                print(f'File my_list_{page}.json created!')
        except IOError as e:
            raise("Error on saving anime list info")
        
        if result['paging'].get('next'):
            new_page = page + 1
            return result['paging']['next'], new_page, response.status_code
        else:
            return None, page, response.status_code
    else:
        print(f'Anormal status {response.status_code}')

def get_anime_list(limit=1,user='@me'):
    # Load environment variables from .env file
    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")
    next_url = f'https://api.myanimelist.net/v2/users/{user}/animelist'
    page = 0
    status_code = 200
    file_path = 'data/raw/anime_list/'
    params = {
        "fields":"list_status",
        "limit": limit
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    while(next_url is not None):
        next_url, page, status_code = get_my_anime_list_page(next_url,headers,page,user,file_path,params=params)

        if status_code == 401:
            token = get_token_myanimelist()
            headers['Authorization'] = f'Bearer {token}'
            print('Get new Token')

    if status_code == 200:
        print('Process Ended in success!')
    else:
        print('Process Ended in error!')

def get_json_files_from_folder(folder_path):
    all_paths = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            all_paths.append(file_path)
    return all_paths

def process_data(data):
    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")
    params = {
        "fields": 'id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,'\
            'nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,'\
            'rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics'
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    file_path = 'data/raw/anime_info/'
    if isinstance(data, list):
        for d in data:
            anime_code = d['node']['id']
            get_anime_info(anime_code,headers,params,file_path)

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            process_data(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")

def get_list_info(folder_anime_list_pages,limit=1,user='@me'):
    get_anime_list(limit=limit, user=user)
    full_path = folder_anime_list_pages + '/' + user
    files = get_json_files_from_folder(full_path)
    for file in files:
        read_json_file(file)


limit = 100
user = 'woterim'
folder_anime_list_pages = 'data/raw/anime_list'

get_list_info(folder_anime_list_pages, limit=limit, user=user)


