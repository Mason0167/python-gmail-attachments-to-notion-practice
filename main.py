from email_handler import *
from attachment_handler import *
from notion_handler import *
from config import *


# Load the state
state = load_state(STATE_FILE)
print("Loaded state:", state)
# Get the set list (unique)
processed_ids = set(state["processed_ids"])
print("Loaded processed_ids:", processed_ids)

# Filter emails then download the attachment
service = get_service(PATH_TO_CREDENTIALS, SCOPES)
messages = get_message(SENDER_ADDRESS, SUBJECT_KEYWORDS, service)

count = 0
for msg in messages:
    
    msg_id = msg["id"]

    if msg_id in processed_ids:
        continue

    attachments = gmail_parser(msg, service)
    # No attachment = skip the mail
    if not attachments:
        continue

    count += 1

    for filename, filedata in attachments:
        if filename.lower().endswith(".p7s"):
            print("Skipping:", filename)
            continue

        download_attachment(filename, filedata, PDF_DIR)

    processed_ids.add(msg_id)

state["processed_ids"] = list(processed_ids)
save_state(state, STATE_FILE)

if count == 0:
    print("\nNo new attachments found.")
else:
    print("\n", count, " new attachments have been downloaded.")



for file_path in PDF_DIR.iterdir():
    if not file_path.is_file():
        continue

    try:
        suffix = file_path.suffix.lower()

        filename = os.path.basename(file_path)
        print("=========================================================================================")
        if suffix == ".pdf":
            if "受託" in filename:
                print("\nProcessing PDF:", file_path)
                trades = parse_USA_pdf(file_path, PDF_PASSWORD)
            else:
                print("\nProcessing PDF:", file_path)
                trades = parse_TW_pdf(file_path, PDF_PASSWORD)

        elif suffix == ".zip":
            print("\nProcessing ZIP:", file_path)
            trades = parse_zip(file_path, PDF_PASSWORD)

        else:
            print("Unknown file type:", file_path)
            continue

        if not trades:
            print("No trades found")
            continue

        success = True

        for trade in trades:
            normalize_trade(trade)
            print("\n", trade)
            create_notion_page(trade, NOTION_TOKEN, DB_ID, filename)

        file_path.unlink()
    
    except Exception as e:
        print("Processing failed:", e)

