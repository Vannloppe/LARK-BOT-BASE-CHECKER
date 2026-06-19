import os
from dotenv import load_dotenv
from lark_client import read_sheet, send_message

load_dotenv()

SPREADSHEET_TOKEN = os.getenv("LARK_SPREADSHEET_TOKEN")
CHAT_ID = os.getenv("LARK_CHAT_ID")

def lambda_handler(event, context):
    """
    AWS Lambda calls THIS function automatically.
    - event: data passed in when Lambda is triggered (we don't need it for scheduled runs)
    - context: AWS runtime info (we don't need it either, but it must be in the signature)
    """
    try:
        # Read rows A1 to D50 from your sheet
        rows = read_sheet(SPREADSHEET_TOKEN, "Sheet1", "A1:D50")
        
        # Example: check if any row has a "PENDING" status in column 3
        alerts = []
        for row in rows:
            if len(row) >= 3 and row[2] == "PENDING":
                alerts.append(f"⚠️ Pending item found: {row[0]}")  # row[0] = column A
        
        if alerts:
            message = "\n".join(alerts)  # join all alerts into one message
            send_message(CHAT_ID, message)
            print(f"Sent alert with {len(alerts)} items")
        else:
            print("No pending items. No alert sent.")
        
        return {"statusCode": 200, "body": "Bot ran successfully"}
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"statusCode": 500, "body": str(e)}