import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

APP_ID     = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")


def get_access_token():
    url     = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id":     APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    data     = response.json()
    return data["tenant_access_token"]


def read_base_records(app_token, table_id):
    token   = get_access_token()
    url     = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}

    all_records = []
    page_token  = None

    while True:
        # ✅ everything in params for GET request
        params = {
            "page_size":        100,
            "field_names":      '["Email Title / Task and Meegle ticket", "Status", "Remarks"]',
            "automatic_fields": "true"   # ← this brings back last_modified_time
        }

        if page_token:
            params["page_token"] = page_token

        response = requests.get(url, headers=headers, params=params)
        data     = response.json()

        if data.get("code") != 0:
            raise Exception(f"Lark Base API error: {data.get('msg')}")

        items = data["data"]["items"]
        all_records.extend(items)

        print(f"Fetched {len(all_records)} records so far...")

        if data["data"].get("has_more"):
            page_token = data["data"].get("page_token")
        else:
            break

    print(f"Total records fetched: {len(all_records)}")
    return all_records


def send_message(chat_id, message):
    token   = get_access_token()
    url     = "https://open.larksuite.com/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }

    content = json.dumps({"text": message})
    payload = {
        "receive_id": chat_id,
        "msg_type":   "text",
        "content":    content
    }
    params   = {"receive_id_type": "chat_id"}
    response = requests.post(url, headers=headers, json=payload, params=params)
    return response.json() 