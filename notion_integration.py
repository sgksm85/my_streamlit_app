import requests
import pandas as pd
from notion_client import Client
from fpdf import FPDF
import streamlit as st
from datetime import datetime
from modules.notion_integration import fetch_work_hours, update_notion_status
from .modules.notion_config import NOTION_API_KEY, NOTION_TIMERECORD_DATABASE_ID

NOTION_API_KEY = "secret_nGXGsWKzJLr1tpbR7kt3eTMVwbfjz9vL4NteDUg2tKc"
NOTION_CLIENT_DATABASE_ID = "ea4dfda2bf074b52a6a3a27a691153d5"
NOTION_PROSPECT_DATABASE_ID = "6ab51c8ae24d4ac49789e69123a42ffc"
NOTION_TODO_DATABASE_ID = "6abab9c4a4374e3db48fcb22f14a1959"
NOTION_PROJECT_DATABASE_ID = "097f9506e00b4b17b0d350bbdfe532d3"
NOTION_TIMERECORD_DATABASE_ID = "4dee3cbe43de46959b496bbb337344b0"
HOURLY_RATE = 2700    

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",  
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def search_database(database_id, keyword):
    query = {
        "filter": {
            "or": [
                {
                    "property": "名前",
                    "title": {
                        "contains": keyword
                    }
                },
                {
                    "property": "カナ",
                    "rich_text": {
                        "contains": keyword
                    }
                }
            ]
        }
    }
    response = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers, json=query)
    
    if response.status_code == 200:
        return response.json().get("results")
    else:
        st.error(f"検索中にエラーが発生しました。ステータスコード: {response.status_code}")
        st.error(f"エラーメッセージ: {response.text}")
        return []

def search_clients(keyword):
    return search_database(NOTION_CLIENT_DATABASE_ID, keyword)

def search_prospects(keyword):
    return search_database(NOTION_PROSPECT_DATABASE_ID, keyword)

def add_to_notion(database, name, kana, notes):
    try:
        database_id = NOTION_CLIENT_DATABASE_ID if database == "クライアント" else NOTION_PROSPECT_DATABASE_ID
        next_number = get_next_number(database)
        
        prefix = "R" if database == "クライアント" else "L"
        client_number = f"{prefix}{next_number}_{name}"

        data = {
        "parent": {"database_id": database_id},
        "properties": {
            "番号": {"number": next_number},
            "名前": {"title": [{"text": {"content": name}}]},
            "カナ": {"rich_text": [{"text": {"content": kana}}]},
            "備考": {"rich_text": [{"text": {"content": notes}}]}
        }
        }
        
        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        return True, next_number, client_number, None
    except requests.exceptions.RequestException as e:
        error_message = f"API Error: {str(e)}"
        if response.text:
            error_message += f"\nResponse: {response.text}"
        return False, None, None, error_message
    except Exception as e:
        return False, None, None, f"Unexpected Error: {str(e)}"

def get_next_number(database):
    database_id = NOTION_CLIENT_DATABASE_ID if database == "クライアント" else NOTION_PROSPECT_DATABASE_ID

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "sorts": [
            {
                "property": "番号",
                "direction": "descending"
            }
        ],
        "page_size": 1
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            last_number = results[0]["properties"]["番号"]["number"]
            return last_number + 1
    return 1  # デフォルト値として1を返す（データがない場合）

def add_to_notion_custom(database_id, **kwargs):
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "名前": {"title": [{"text": {"content": kwargs.get("name", "")}}]},
            "進捗状況": {"status": {"name": kwargs.get("status", "")}},
        }
    }

    if "tags" in kwargs and kwargs["tags"]:
        data["properties"]["タグ"] = {"multi_select": [{"name": tag} for tag in kwargs["tags"]]}
    
    if "tag2" in kwargs and kwargs["tag2"]:
        data["properties"]["タグ 2"] = {"select": {"name": kwargs["tag2"]}}
    
    if "url" in kwargs and kwargs["url"]:
        data["properties"]["URL"] = {"url": kwargs["url"]}
    
    if "notes" in kwargs and kwargs["notes"]:
        data["properties"]["備考"] = {"rich_text": [{"text": {"content": kwargs["notes"]}}]}

    try:
        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        response.raise_for_status()
        return True, None
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_message += f"\nResponse Text: {e.response.text}"
        return False, error_message

def get_select_options(database_id, property_name):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        properties = response.json().get("properties")
        if properties and property_name in properties:
            prop = properties[property_name]
            if prop["type"] == "select":
                return [option["name"] for option in prop["select"]["options"]]
    return []

def search_todo_or_project_database(database_id):

    query = {}
    response = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers, json=query)
    
    if response.status_code == 200:
        return response.json().get("results")
    else:
        return []

def fetch_work_hours(start_date=None, end_date=None):
    client = Client(auth=NOTION_API_KEY)
    database_id = NOTION_TIMERECORD_DATABASE_ID
    
    work_hours_data = []
    has_more = True
    start_cursor = None
    
    while has_more:
        query_params = {'page_size': 100}
        if start_cursor:
            query_params['start_cursor'] = start_cursor
        
        if start_date and end_date:
            query_params['filter'] = {
                'and': [
                    {
                        'property': '開始',
                        'date': {'on_or_after': start_date.isoformat()}
                    },
                    {
                        'property': '終了',
                        'date': {'on_or_before': end_date.isoformat()}
                    }
                ]
            }
            
        query = client.databases.query(database_id=database_id, **query_params)
        
        for record in query.get('results', []):
            properties = record.get('properties', {})
            
            start_time_prop = properties.get('開始', {}).get('date', {})
            end_time_prop = properties.get('終了', {}).get('date', {})
            
            if not start_time_prop or not end_time_prop:
                continue
            
            start_time_str = start_time_prop.get('start')
            end_time_str = end_time_prop.get('start')
            
            if not start_time_str or not end_time_str:
                continue
            
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', ''))
                end_time = datetime.fromisoformat(end_time_str.replace('Z', ''))
                
                work_duration = end_time - start_time
                hours, remainder = divmod(work_duration.seconds, 3600)
                minutes = remainder // 60
                
                work_hours_data.append({
                    "日付": start_time.strftime("%Y/%m/%d"),
                    "開始時間": start_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "終了時間": end_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "労働時間": f"{hours:02d}:{minutes:02d}",
                    "Page ID": record.get('id'),
                    "ステータス": properties.get('Status', {}).get('status', {}).get('name', '未請求')
                })
            except (ValueError, AttributeError) as e:
                print(f"Error processing record: {e}")
                continue
        
        has_more = query.get('has_more', False)
        start_cursor = query.get('next_cursor')
    
    work_hours_data.sort(key=lambda x: datetime.strptime(x["日付"], "%Y/%m/%d"))
    return work_hours_data

def update_notion_status(page_id, status):
    client = Client(auth=NOTION_API_KEY)
    client.pages.update(
        page_id=page_id,
        properties={
            'Status': {
                'status': {'name': status}
            }
        }
    )
