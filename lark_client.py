from email import message

import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()  # loads your .env file so os.getenv() can read it

APP_ID = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")

def get_access_token():
    """
    Every Lark API call needs a token first.
    Think of it like logging in before you can do anything.
    """
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    response = requests.post(url, json=payload)  # json= auto-converts dict to JSON
    data = response.json()                        # converts response back to Python dict
    
    return data["tenant_access_token"]           # return just the token string


def read_base_records(app_token, table_id):
    """
    Reads records from a Lark Base table.
    This is different from Sheets — Base returns 'records' not 'rows'
    Each record has a 'fields' object containing all your column values
    """
    token = get_access_token()

    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # you can filter, sort, or limit records here
    params = {
        "page_size": 100,
        "field_names": '["Email Title / Task and Meegle ticket", "Status", "Remarks"]',
        "with_shared_url": "false",
        "automatic_fields": "true"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    print(f"API Response: {data}")  # helpful for debugging

    if data.get("code") != 0:
        raise Exception(f"Lark Base API error: {data.get('msg')}")

    return data["data"]["items"]  # returns list of records

def send_message(chat_id, message):
    """
    Sends a text message to a Lark chat group or user.
    """
    token = get_access_token()
    
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    content = json.dumps({"text": message})
    print(f"DEBUG content: {content}")  # ← see exactly what's being sent

    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": content
    }
    
    params = {"receive_id_type": "chat_id"}  # tells Lark the ID is a group chat
    
    response = requests.post(url, headers=headers, json=payload, params=params)
    return response.json()