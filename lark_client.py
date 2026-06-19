import requests
import os
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


def read_sheet(spreadsheet_token, sheet_id, range):
    """
    Reads data from a specific range in your Lark Sheet.
    range example: "A1:D10" (like Excel/Google Sheets)
    """
    token = get_access_token()
    
    url = f"https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}!{range}"
    
    headers = {
        "Authorization": f"Bearer {token}"  # tells Lark "hey, I'm logged in"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return data["data"]["valueRange"]["values"]  # returns a list of rows


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
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": f'{{"text": "{message}"}}'  # Lark requires this exact format
    }
    
    params = {"receive_id_type": "chat_id"}  # tells Lark the ID is a group chat
    
    response = requests.post(url, headers=headers, json=payload, params=params)
    return response.json()