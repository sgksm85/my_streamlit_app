import requests
from notion_client import Client, APIResponseError
from datetime import datetime, timedelta
from .notion_config import (
    NOTION_API_KEY, 
    NOTION_CLIENT_DATABASE_ID, 
    NOTION_PROSPECT_DATABASE_ID,
    NOTION_TIMERECORD_DATABASE_ID
)

# Notionクライアントを初期化
notion_client = Client(auth=NOTION_API_KEY)

# NotionのAPIリクエストに必要なヘッダー情報
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
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
    response = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=HEADERS, json=query)
    
    if response.status_code == 200:
        return response.json().get("results")
    else:
        return []

def search_clients(keyword):
    try:
        response = notion_client.databases.query(
            **{
                "database_id": NOTION_CLIENT_DATABASE_ID,
                "filter": {
                    "property": "名前",
                    "rich_text": {
                        "contains": keyword
                    }
                }
            }
        )
        return response['results']
    except APIResponseError as e:
        return []

def search_prospects(keyword):
    try:
        response = notion_client.databases.query(
            **{
                "database_id": NOTION_PROSPECT_DATABASE_ID,
                "filter": {
                    "property": "名前",
                    "rich_text": {
                        "contains": keyword
                    }
                }
            }
        )
        return response['results']
    except APIResponseError as e:
        return []

def add_to_notion(database, name, kana, notes):
    database_id = NOTION_CLIENT_DATABASE_ID if database == "クライアント" else NOTION_PROSPECT_DATABASE_ID
    try:
        response = notion_client.pages.create(
            parent={"database_id": database_id},
            properties={
                "名前": {"title": [{"text": {"content": name}}]},
                "カナ": {"rich_text": [{"text": {"content": kana}}]},
                "備考": {"rich_text": [{"text": {"content": notes}}]}
            }
        )
        return True, response['properties']['番号']['number'], response['properties']['クライアント番号']['formula']['string'], None
    except APIResponseError as e:
        return False, None, None, str(e)

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

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            last_number = results[0]["properties"]["番号"]["number"]
            return last_number + 1
    return 1

def get_database_schema(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["properties"]
    return {}

def add_to_notion_custom(database_id, **kwargs):
    notion_database_schema = get_database_schema(database_id)
    
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
    
    # Start Date と Due Date を追加
    if "start_date" in kwargs and kwargs["start_date"]:
        data["properties"]["Start Date"] = {"date": {"start": kwargs["start_date"].isoformat()}}
    
    if "due_date" in kwargs and kwargs["due_date"]:
        data["properties"]["Due Date"] = {"date": {"start": kwargs["due_date"].isoformat()}}

    try:
        response = requests.post('https://api.notion.com/v1/pages', headers=HEADERS, json=data)
        response.raise_for_status()
        return True, None
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_message += f"\nResponse Text: {e.response.text}"
        return False, error_message
    
def get_select_options(database_id, property_name):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        properties = response.json().get("properties")
        if properties and property_name in properties:
            prop = properties[property_name]
            if prop["type"] == "select":
                return [option["name"] for option in prop["select"]["options"]]
    return []

def search_todo_or_project_database(database_id):
    query = {}
    response = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=HEADERS, json=query)
    
    if response.status_code == 200:
        return response.json().get("results")
    else:
        return []

def fetch_work_hours(start_date=None, end_date=None):
    # Notionクライアントを初期化
    client = Client(auth=NOTION_API_KEY)
    database_id = NOTION_TIMERECORD_DATABASE_ID
    
    work_hours_data = []  # 労働時間データを格納するリスト
    has_more = True  # まだデータがあるかどうかのフラグ
    start_cursor = None  # ページネーションのためのカーソル
    
    while has_more:
        # Notionデータベースに対してクエリを実行
        query_params = {'page_size': 100}  # 一度に取得するレコード数
        if start_cursor:
            query_params['start_cursor'] = start_cursor
        
        query = client.databases.query(database_id=database_id, **query_params)
        
        for record in query.get('results', []):
            properties = record.get('properties', {})
            
            # 開始時間と終了時間を取得
            start_time_prop = properties.get('開始', {}).get('date', {})
            end_time_prop = properties.get('終了', {}).get('date', {})
            
            if not start_time_prop or not end_time_prop:
                continue
            
            start_time_str = start_time_prop.get('start')
            end_time_str = end_time_prop.get('start')
            
            if not start_time_str or not end_time_str:
                continue
            
            try:
                # 文字列を日時オブジェクトに変換
                start_time = datetime.fromisoformat(start_time_str.replace('Z', ''))
                end_time = datetime.fromisoformat(end_time_str.replace('Z', ''))
                
                # 指定された日付範囲内かどうかをチェック
                if start_date and start_time.date() < start_date:
                    continue
                if end_date and end_time.date() > end_date:
                    continue
                
                # 労働時間を計算
                work_duration = end_time - start_time
                hours, remainder = divmod(work_duration.seconds, 3600)
                minutes = remainder // 60
                
                # データを整形してリストに追加
                work_hours_data.append({
                    "日付": start_time.strftime("%Y/%m/%d"),
                    "開始時間": start_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "終了時間": end_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "労働時間": f"{hours:02d}:{minutes:02d}",
                    "Page ID": record.get('id'),
                    "ステータス": properties.get('請求状況', {}).get('select', {}).get('name', '未請求')
                })
            except (ValueError, AttributeError) as e:
                print(f"レコード処理中にエラーが発生しました: {e}")
                continue
        
        # 次のページがあるかどうかをチェック
        has_more = query.get('has_more', False)
        start_cursor = query.get('next_cursor')
    
    # 日付順にソート
    work_hours_data.sort(key=lambda x: datetime.strptime(x["日付"], "%Y/%m/%d"))
    return work_hours_data

def update_notion_custom(database_id, page_id, name, status, start_date, due_date, url):
    try:
        response = notion_client.pages.update(
            page_id,
            properties={
                "名前": {"title": [{"text": {"content": name}}]},
                "進捗状況": {"status": {"name": status}},
                "Start Date": {"date": {"start": start_date.isoformat()} if start_date else None},
                "Due Date": {"date": {"start": due_date.isoformat()} if due_date else None},
                "URL": {"url": url if url else None}
            }
        )
        return True, None
    except APIResponseError as e:
        return False, str(e)

def update_notion_status(page_id, status):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": {
            "請求状況": {"status": {"name": status}}
        }
    }
    
    print(f"リクエストURL: {url}")
    print(f"リクエストデータ: {data}")
    print(f"ヘッダー: {HEADERS}")

    try:
        response = requests.patch(url, headers=HEADERS, json=data)
        print(f"レスポンスステータスコド: {response.status_code}")
        print(f"レスポンス内容: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")
        raise

def calculate_total_hours(work_hours_data):
    # 総労働時間を秒単位で計算
    total_seconds = sum(
        (datetime.strptime(entry["終了時間"], "%Y/%m/%d %H:%M:%S") - 
         datetime.strptime(entry["開始時間"], "%Y/%m/%d %H:%M:%S")).total_seconds()
        for entry in work_hours_data
    )
    # 秒を時間と分に変換
    total_hours, remainder = divmod(total_seconds, 3600)
    total_minutes = remainder // 60
    return f"{int(total_hours)}時間{int(total_minutes)}分"

__all__ = [
    'add_to_notion_custom',
    'search_todo_or_project_database',
    'fetch_work_hours',
    'calculate_total_hours',
    'update_notion_status'
]