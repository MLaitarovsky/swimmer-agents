import pdfplumber
import pandas as pd
import re
import os

# Configuration
PDF_FOLDER = "pdfs"  # Folder where you put all your uploaded PDF files
OUTPUT_FILE = "all_swimmers_raw.csv"

# Common Hebrew words in club names to filter out
CLUB_BLACKLIST = [
    "מכבי",
    "הפועל",
    "ירושלים",
    "תל אביב",
    "חיפה",
    "נתניה",
    "אגודה",
    "שחייה",
    "בת ים",
    "קרית",
    "אתא",
    "עמק",
    "חפר",
    "הוד",
    "השרון",
    "בני",
    "הרצליה",
    "יזרעאל",
    "גליל",
    "עליון",
    "ראשון",
    "לציון",
    "אילת",
    'אס"א',
    "כפר",
    "סבא",
    "רעות",
    "מודיעין",
    "פארק",
    "המים",
    "עומר",
    "משגב",
    "דולפין",
    "אשדוד",
    "אשקלון",
    "רמת",
    "גן",
    "גבעתיים",
    "יבנה",
    "נס",
    "ציונה",
]


def is_valid_name(text):
    """
    Checks if a string is likely a human name and not a club or junk.
    """
    if not text:
        return False

    # Clean text
    text = text.strip()

    # Must be at least 2 words (First + Last)
    if len(text.split()) < 2:
        return False

    # Must contain only Hebrew letters and spaces
    if not re.match(r'^[\u0590-\u05FF\s"\'-]+$', text):
        return False

    # Check against blacklist (if it contains club words)
    for bad_word in CLUB_BLACKLIST:
        if bad_word in text:
            return False

    return True


def extract_names_from_pdf(pdf_path):
    found_names = set()
    print(f"📄 Processing: {os.path.basename(pdf_path)}...")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    # Filter None values and empty strings
                    row = [str(cell).strip() for cell in row if cell]

                    # Logic: In swimming results, the Name is usually the
                    # first "text-heavy" column that ISN'T a club.
                    for cell in row:
                        if is_valid_name(cell):
                            found_names.add(cell)

    return found_names


def main():
    all_unique_swimmers = set()

    # Ensure PDF folder exists
    if not os.path.exists(PDF_FOLDER):
        print(
            f"❌ Error: Folder '{PDF_FOLDER}' not found. Please create it and add your PDFs."
        )
        return

    # Iterate over all PDF files
    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    print(f"🔍 Found {len(files)} PDF files.")

    for filename in files:
        path = os.path.join(PDF_FOLDER, filename)
        names = extract_names_from_pdf(path)
        all_unique_swimmers.update(names)
        print(f"   -> Found {len(names)} unique names in this file.")

    # Export to CSV
    df = pd.DataFrame(sorted(list(all_unique_swimmers)), columns=["Name"])
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n✅ DONE! Extracted {len(df)} unique swimmers.")
    print(f"💾 Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
