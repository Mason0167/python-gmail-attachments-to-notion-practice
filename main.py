from email_handler import *
from attachment_handler import *
from notion_handler import *
from config import *


# Get data from gmail source
def fetch_from_gmail(messages, service):
    attachment_count = 0
    for msg in messages:

        # Skip if the mail had been processed
        msg_id = msg["id"]
        if msg_id in processed_ids:
            continue

        # Count how many new attachment
        attachment_count += 1

        # Store the id 
        processed_ids.add(msg_id)

        # Fetch the attachment
        attachments = gmail_parser(msg, service)
        
        # Skip if the mail has no attachment
        if not attachments:
            continue

        # Stop and give a value
        for filename, filedata in attachments:
            yield filename, filedata
    
    if attachment_count == 0:
        print("\nNo new attachments found.")
    else:
        print(attachment_count, " new attachments were found.")

    print("=========================================================================================")


# Get data from directory source (failed items)
def fetch_from_dir(PDF_DIR):
    # Check item
    if not any(PDF_DIR.iterdir()):
        return
    
    for file_path in PDF_DIR.iterdir():
        print(file_path)
        # Check if the path exist and if it's a regular file
        if not file_path.is_file():
            continue

        # Skip S/MIME
        if file_path.name.lower().endswith(".p7s"):
            print("Skipping:", file_path.name)
            continue

        # Read the binary file
        with open(file_path, "rb") as f:
            filedata = f.read()

        yield file_path.name, filedata

def process_file(filename, filedata):
    filename = Path(filename)

    try:
        suffix = filename.suffix.lower()

        if suffix == ".pdf":

            if "受託" in filename.name:
                print("Processing PDF:", filename.name)
                print("=========================================================================================")

                trades = parse_USA_pdf(filedata, PDF_PASSWORD)
            else:
                print("Processing PDF:", filename.name)
                print("=========================================================================================")

                trades = parse_TW_pdf(filedata, filename.name, PDF_PASSWORD)

        elif suffix == ".zip":
            print("Processing ZIP:", filename.name)
            print("=========================================================================================")

            trades = parse_zip(filedata, filename.name, PDF_PASSWORD)

        elif suffix == ".p7s":
            return

        else:
            print("Unknown file type:", filename.name)
            print("=========================================================================================")
            return

        if not trades:
            print("No trades found")
            return
        
        totalCount = 0
        successCount = 0
        failedCount = 0

        for trade in trades:
            normalize_trade(trade)
            print(trade)

            res = create_notion_page(trade, NOTION_TOKEN, DB_ID)

            totalCount += 1

            # Process both success and failed item
            failed_item = {}
            if res.status_code >= 400:
                failed_item = {
                    "Trade File": filename.name,
                    "Trade": trade, 
                    "Error Text": res.text
                }
                process_failed_item(failed_item)
                failedCount += 1
                print("This item has failed.")

            elif res.status_code == 200:
                successCount += 1
                print("This item has succeeded.")

            print("=========================================================================================")

        print("Total processed trade: ",  totalCount)
        print("Success trade: ", successCount)
        print("Failed trade: ", failedCount)
        print("=========================================================================================")



    except Exception as e:
        print("Failed:", e)
        download_attachment(filename, filedata, PDF_DIR)


'''
===== Main Process =====
'''
# Load the state
state = load_state(STATE_FILE)

# Get the set list (unique)
processed_ids = set(state["processed_ids"])
print("Loaded processed_ids:", processed_ids, "\n")

# Filter emails
service = get_service(PATH_TO_CREDENTIALS, SCOPES)
messages = get_message(SENDER_ADDRESS, SUBJECT_KEYWORDS, service)

# Choose source
print("Processing ", processed_ids)
source = fetch_from_gmail(messages, service)

source = fetch_from_dir(PDF_DIR)

for filename, filedata in source:
    process_file(filename, filedata)

# Save the mail id which are processed
state["processed_ids"] = list(processed_ids)
save_state(state, STATE_FILE)
