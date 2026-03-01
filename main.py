from email_handler import *
from attachment_handler import *
from notion_handler import *
from config import *

# # Load the state
# state = load_state(STATE_FILE)
# processed_ids = set(state["processed_ids"])

# # Filter emails then download the attachment
# service = get_service(PATH, SCOPES)
# messages = get_message(SENDER_ADDRESS, SUBJECT_KEYWORDS, service)

# count = 0
# for msg in messages:
#     msg_id = msg["id"]

#     if msg_id in processed_ids:
#         continue

#     result = gmail_parser(msg, service)
#     if not result:
#         continue

#     count += 1
#     filename, filedata = result
        
#     download_attachment(filename, filedata, PDF_DIR)

#     processed_ids.add(msg_id)

# state["processed_ids"] = list(processed_ids)
# save_state(state, STATE_FILE)

# if count == 0:
#     print("\nNo new attachments found.")
# else:
#     print("\n", count, " new attachments have been downloaded.")



for file_path in PDF_DIR.iterdir():
    if not file_path.is_file():
        continue

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
        print("\nProcessing PDF:", file_path)
        trades = parse_zip(file_path, PDF_PASSWORD)

    for trade in trades:
        normalize_trade(trade)
        print("\n", trade)
        create_notion_page(trade, NOTION_TOKEN, DB_ID, filename)

1. Create a function for documenting the trade record information that is failed to insert into Notion. 2. Print important messages in terminal for better understanding the current program status. 3. Save all email id that processed was before.