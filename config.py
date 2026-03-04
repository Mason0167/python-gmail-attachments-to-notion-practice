from secret import *
from pathlib import Path

# List of permission scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SENDER_ADDRESS = "service@billu.tssco.com.tw"
SUBJECT_KEYWORDS = [
    "台新證券電子月對帳單",
    "台新綜合證券",
    "台新證券受託買賣外國有價證券確認書"
]
PDF_DIR = Path("transaction_records")
STATE_FILE = "state.json"
FAILED_TRADE_FILE = "failed_trades.json"

PDF_PASSWORD = PDF_PASSWORD_SECRET
# Path to credentials.json, which I downloaded from Google
PATH_TO_CREDENTIALS = PATH_TO_CREDENTIALS_SECRET
NOTION_TOKEN = NOTION_TOKEN_SECRET
DB_ID = DB_ID_SECRET
