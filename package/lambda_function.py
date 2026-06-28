import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from lark_client import read_base_records, send_message

load_dotenv()

APP_TOKEN = os.getenv("LARK_BASE_APP_TOKEN")
TABLE_ID  = os.getenv("LARK_BASE_TABLE_ID")
CHAT_ID   = os.getenv("LARK_CHAT_ID")

TABLES = [
    {
        "table_id": os.getenv("LARK_BASE_TABLE_ID_1"),
        "name":     os.getenv("LARK_BASE_TABLE_NAME_1")
    },
    {
        "table_id": os.getenv("LARK_BASE_TABLE_ID_2"),
        "name":     os.getenv("LARK_BASE_TABLE_NAME_2")
    },
]



def lambda_handler(event, context):
    try:
        eight_hrs_ago = datetime.now(tz=timezone.utc) - timedelta(hours=8)
        alerts= []

        for table in TABLES:
            print(f"Checking table: {table['name']}")
            records = read_base_records(APP_TOKEN, table["table_id"])

            
        # debug — print first record's exact field names
        if records:
            first = records[0].get("fields", {})

        for record in records:
            record_fields = record.get("fields", {})
            modified_time = record.get("last_modified_time")
            
        
            # skip completely empty records
            if not record_fields:
                continue
            
            task    = record_fields.get("Email Title / Task and Meegle ticket")
            status  = record_fields.get("Status")
            remarks = record_fields.get("Remarks")
            
            # skip if both task and remarks are missing
            if not task and not remarks:
                continue

            # skip if status is closed or done
            if status in ["Case Closed", "Done","Assigned to DEV/PO"]:
                continue

            if task in ["DO NOT REMOVE"]:
                continue

            print(f"DEBUG task: {task}, status: {status}, remarks: {remarks}, modified_time: {modified_time}")

            if modified_time:
                modified_dt = datetime.fromtimestamp(modified_time / 1000, tz=timezone.utc)
                
                print(f"Current UTC Time: {datetime.now(timezone.utc)}")
                print(f"Cutoff Time:      {eight_hrs_ago}")
                print(f"Modified Time:    {modified_dt}")
                print(f"Comparison:       {modified_dt < eight_hrs_ago}")
                
                
                
                if modified_dt < eight_hrs_ago:
                    alerts.append(
                        f"===============================\n"
                        f"🔔 Record needs update!\n"
                        f"Table: {table['name']}\n"
                        f"Task: {task}\n"
                        f"Status: {status}\n"
                        f"Remarks: {remarks}\n"
                        f"Last updated: {modified_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                        f"\n==============================="
                    )

        if alerts:
            message = "\n\n".join(alerts)  # ← double newline so each alert is separated
            send_message(CHAT_ID, message)
            print(f"Sent {len(alerts)} alerts")
        else:
            print("No records need updating")
            send_message(os.getenv("LARK_CHAT_ID"), "✅ No records need updating in the last 8 hours.")

        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"statusCode": 500, "body": str(e)}