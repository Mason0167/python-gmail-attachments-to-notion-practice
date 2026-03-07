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

def get_service(PATH_TO_CREDENTIALS, SCOPES):
    # This initializes an OAuth 2.0 authorization flow for installed applications.
    flow = InstalledAppFlow.from_client_secrets_file(PATH_TO_CREDENTIALS, SCOPES)

    # Opens a browser window > Log in and grant permission > Receives the authorization code > Exchanges it for an access token and refresh token
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def get_message(SENDER_ADDRESS, SUBJECT_KEYWORDS, service):
    # Combine keywords into one query using OR
    # Unseen email: f'from:{SENDER_ADDRESS} is:unread'
    query = f'from:{SENDER_ADDRESS} (' + \
        " OR ".join([f'subject:\"{k}\"' for k in SUBJECT_KEYWORDS]) + \
        ')'

    # API call
    # List messages matching query
    results = service.users().messages().list(
        # Refers to the authenticated user
        userId='me', 
        q=query
    ).execute()

    # messages is a list of dicts with id of each email matching the query
    return results.get('messages', [])

# This recursively walks the entire MIME tree.
def iter_parts(part): 
    yield part 
    for sub in part.get("parts", []): 
        yield from iter_parts(sub)

def gmail_parser(msg, service):
        # Extract the unique Gmail message ID
        msg_id = msg['id']
        message = service.users().messages().get(
            userId='me', 
            id=msg_id, 
            # format='full' 
            # returns: headers, body, full MIME structure, attachment references
            format='full'
        ).execute()
        
        # payload includes：
        # headers（From / To / Subject）
        # body（文字或 HTML）
        # parts（附件與子內容）
        payload = message["payload"]
        attachments = []

        # Traverse All MIME Parts
        for part in iter_parts(payload):
            filename = part.get("filename")
            body = part.get("body", {})

            if not filename:
                continue

            # Small attachment
            if "data" in body:
                # Decode
                filedata = base64.urlsafe_b64decode(body["data"])

            # Large attachment
            elif "attachmentId" in body:
                attachment = service.users().messages().attachments().get(
                    userId="me",
                    messageId=msg_id,
                    id=body["attachmentId"]
                ).execute()
                filedata = base64.urlsafe_b64decode(attachment["data"])
            else:
                continue
            
            # Store multiple attachments
            attachments.append((filename, filedata))

        return attachments if attachments else None
