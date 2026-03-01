from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import json
import os

def load_state(STATE_FILE):
    if not os.path.exists(STATE_FILE):
        return {"processed_ids": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state, STATE_FILE):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_service(PATH, SCOPES):
    flow = InstalledAppFlow.from_client_secrets_file(PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def get_message(SENDER_ADDRESS, SUBJECT_KEYWORDS, service):

    # Combine keywords into one query using OR
    # Unseen email: f'from:{SENDER_ADDRESS} is:unread'
    query = f'from:{SENDER_ADDRESS} ' + \
        " OR ".join([f'subject:"{k}"' for k in SUBJECT_KEYWORDS])

    # List messages matching query
    results = service.users().messages().list(
        userId='me', 
        q=query
    ).execute()

    # messages is a list of dicts with id of each email matching the query
    return results.get('messages', [])


def iter_parts(part): 
    yield part 
    for sub in part.get("parts", []): 
        yield from iter_parts(sub)

def gmail_parser(msg, service):
        msg_id = msg['id']
        message = service.users().messages().get(
            userId='me', 
            id=msg_id, 
            format='full'
        ).execute()
        
        # payload 包含：
        # headers（From / To / Subject）
        # body（文字或 HTML）
        # parts（附件與子內容）
        payload = message["payload"]

        for part in iter_parts(payload):
            filename = part.get("filename")
            body = part.get("body", {})

            if not filename:
                continue

            if "data" in body:
                filedata = base64.urlsafe_b64decode(attachment["data"])

            if "attachmentId" in body:
                attachment_id = body["attachmentId"]
                attachment = service.users().messages().attachments().get(
                    userId="me",
                    messageId=msg_id,
                    id=attachment_id
                ).execute()
                filedata = base64.urlsafe_b64decode(attachment["data"])
            else:
                continue
            
            return filename, filedata
            
        return None