import pdfplumber
import os

PDF_FOLDER = "pdfs"


def debug_first_page():
    # מוצא קובץ PDF ראשון בתיקייה
    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if not files:
        print("No PDFs found!")
        return

    test_file = os.path.join(PDF_FOLDER, files[0])
    print(f"🕵️ Debugging file: {test_file}")

    with pdfplumber.open(test_file) as pdf:
        first_page = pdf.pages[0]

        # 1. נסה להדפיס טקסט גולמי
        print("\n--- RAW TEXT SAMPLE (First 500 chars) ---")
        text = first_page.extract_text()
        if text:
            print(text[:500])
        else:
            print("❌ No text extracted (Might be an image scan?)")

        # 2. נסה להדפיס שורה ראשונה בטבלה
        print("\n--- TABLE SAMPLE ---")
        tables = first_page.extract_tables()
        if tables:
            print(f"Found {len(tables)} tables.")
            if tables[0]:
                print("First row of first table:")
                print(tables[0][0])  # מדפיס את השורה הראשונה
        else:
            print("❌ No tables detected using default settings.")


if __name__ == "__main__":
    debug_first_page()
