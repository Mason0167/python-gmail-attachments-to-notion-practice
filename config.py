from secret import *
from pathlib import Path

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
PATH = PATH_SECRET
NOTION_TOKEN = NOTION_TOKEN_SECRET
DB_ID = DB_ID_SECRET
