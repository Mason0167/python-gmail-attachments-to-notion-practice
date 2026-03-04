# Gmail-to-Notion Trade Automation
A Python automation pipeline that retrieves financial transaction emails from Gmail, extracts trade data from PDF/ZIP attachments, and inserts structured records into a Notion database.

The system includes duplicate prevention, state tracking, and error logging for failed inserts.


## Architecture

Gmail API → Attachment Parser → Data Transformation → Notion API


## Features

- Gmail API integration
- Attachment parsing (PDF / ZIP)
- Automated Notion database insertion
- Duplicate email detection using message IDs
- Failed insert logging


## State Management

Processed email IDs are stored in `state.json` to prevent duplicate processing.

Failed insert records are stored in `failed_trades.json`.
