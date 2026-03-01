import requests
import json
import os
from datetime import date
from config import FAILED_TRADE_FILE

def process_failed_item(failed_item):
    # 1. 檢查檔案是否存在，如果存在則讀取舊資料
    if os.path.exists(FAILED_TRADE_FILE):
        with open(FAILED_TRADE_FILE, "r", encoding="utf-8") as f:
            try:
                # 讀取並解析成 Python List 或 Dict
                data = json.load(f)

            except json.JSONDecodeError:
                # 如果檔案是空的或損毀，初始化為 List
                data = []
    else:
        data = []

    # 2. 將新資料追加到 List 中 (假設你的 JSON 根節點是 List)
    if not isinstance(data, list):
        data = []
    
    data.append(failed_item)

    with open(FAILED_TRADE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        print("Failed trade record has stored")



def create_notion_page(trade: dict, NOTION_TOKEN, DB_ID, filename):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    data = {
        "parent": {"database_id": DB_ID},
        "properties": {
            "Ticker": {
                "title": [{"text": {"content": trade["Ticker"]}}]
            },
            "Company Name": {
                "rich_text": [{"text": {"content": trade["Company Name"]}}]
            },
            "Broker": {
                "rich_text": [{"text": {"content": "台新證券"}}]
            },
            "Side": {"select": {"name": trade["Side"]}},
            "Quantity": {"number": trade["Quantity"]},
            "Execution Price": {"number": trade["Execution Price"]},
            "Commission": {"number": trade["Commission"]},
            "Tax": {"number": trade["Tax"]},
            "Currency": {"select": {"name": trade["Currency"]}},
            "Total Amount": {"number": trade["Total Amount"]},
            "Trade Date": {
                "date": {"start": trade["Trade Date"], "end": None}
            }
        }
    }

    res = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    failed_item = {}
    if res.status_code >= 400:
        failed_item = {
            "Trade File": filename,
            "Trade": trade, 
            "Error Text": res.text
        }
        process_failed_item(failed_item)

    elif res.status_code == 200:
        print(res.status_code)
    print("------------------------")



def normalize_trade(trade: dict) -> dict:
    TaxValue = trade.get("Tax")
    trade["Tax"] = int(TaxValue)
    
    # 如果沒給預設值，預設回傳 None
    TradeYear, TradeMonth, TradeDay = trade.get("Trade Date").split("/")
    if "@" in TradeDay:
        TradeDay = TradeDay.strip("@")
    trade["Trade Date"] = date(int(TradeYear), int(TradeMonth), int(TradeDay)).isoformat()


    if "," in trade["Quantity"]:
        Qty = trade["Quantity"].replace(",", "")
        trade["Quantity"] = float(Qty)
    else:
        trade["Quantity"] = float(trade["Quantity"])

    trade["Execution Price"] = float(trade["Execution Price"])
    trade["Commission"] = float(trade["Commission"])

    if '現買' in trade["Side"] or '-' in trade["Side"]:
        trade["Side"] = "Buy"
    else:
        trade["Side"] = "Sell"

    if "(" in trade["Ticker"]:
        trade["Ticker"] = trade["Ticker"].strip("()")

    TotalAmount = trade["Total Amount"].replace(",", "")
    trade["Total Amount"] = float(TotalAmount)

    return {
        "Currency": trade["Currency"],
        "Tax": trade["Tax"],
        "Trade Date": trade["Trade Date"],
        "Ticker": trade["Ticker"],
        "Quantity": trade["Quantity"],
        "Execution Price": trade["Execution Price"],
        "Commission": trade["Commission"],
        "Side": trade["Side"],
        "Company Name": trade["Company Name"],
        "Total Amount": trade["Total Amount"]
    }