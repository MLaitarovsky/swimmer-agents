import pdfplumber
import pandas as pd
import re
import os

# Configuration
PDF_FOLDER = 'pdfs'
OUTPUT_FILE = 'all_swimmers_cleaned.csv'

# 🛑 SUPER BLACKLIST
# Contains every club part, city, and non-name word we saw in your errors.
BLACKLIST = [
    # --- Clubs & Organizations ---
    'מכבי', 'הפועל', 'אגודת', 'אגודות', 'איגוד', 'השחייה', 'שחייני', 'שחיין',
    'מכון', 'וינגייט', 'אולימפ', 'ספורטן', 'פליפר', 'אס"א', 'עצמה',
    'פארק', 'המים', 'רעות', 'דולפין', 'יוני', 'ספיד', 'גל', 'גלי',
    'מועדון', 'ספורט', 'מתנס', 'מתנ"ס', 'בית', 'לוחם', 'הנכים',
    
    # --- Cities & Locations (Single & Combined) ---
    'ירושלים', 'תל', 'אביב', 'תלאביב', 'חיפה', 'נתניה', 'הרצליה',
    'בני', 'הרצליה', 'רעננה', 'כפר', 'סבא', 'כפרסבא', 'הוד', 'השרון',
    'קרית', 'אונו', 'ביאליק', 'מוצקין', 'אתא', 'טבעון', 'יקנעם',
    'משגב', 'עמק', 'חפר', 'יזרעאל', 'גליל', 'עליון', 'ראשון', 'לציון',
    'ראשלצ', 'רחובות', 'וייסגל', 'נס', 'ציונה', 'יבנה', 'אשדוד', 'אשקלון',
    'באר', 'שבע', 'בארשבע', 'הנגב', 'עומר', 'אילת', 'גדרות', 'שוהם',
    'מודיעין', 'מכבים', 'רעות', 'בית', 'שמש', 'ירוחם', 'להבים',
    'נצרת', 'סכנין', 'רמת', 'גן', 'רמתגן', 'גבעתיים', 'פתח', 'תקוה', 'פתחתקוה',
    'בת', 'ים', 'בתים', 'חולון', 'אזור', 'גזר', 'מעלה', 'אדומים',
    
    # --- Common Terms in Tables ---
    'עירוני', 'רבתי', 'מרכז', 'אקדמיה', 'הפנימייה', 'בוגרים', 'נוער', 'צעירים',
    'אליפות', 'ישראל', 'גביע', 'מדינה', 'חורף', 'קיץ', 'מוקדמות', 'גמר',
    'חצי', 'משחה', 'מקצה', 'מסלול', 'תוצאה', 'ניקוד', 'כללי', 'סופי',
    'זמן', 'תגובה', 'שנת', 'לידה', 'דרגה', 'שם', 'פרטי', 'משפחה',
    'SUMMARY', 'Results', 'Heat', 'Lane', 'Rank', 'Club', 'Name'
]

def reverse_hebrew(text):
    """ Fixes visual Hebrew (turns 'םולש' into 'שלום') """
    return text[::-1]

def is_valid_word(word):
    """ Check if a specific word is a valid name part """
    if len(word) < 2: 
        return False
    if re.search(r'\d', word): # No numbers
        return False
    
    # Clean quotes/punctuation
    clean = word.replace('"', '').replace("'", "").replace("-", "")
    
    # Check against blacklist (Regular AND Reversed)
    for bad in BLACKLIST:
        if bad == clean or bad == reverse_hebrew(clean):
            return False
            
    return True

def parse_line(line):
    words = line.split()
    clean_words = []
    
    for word in words:
        # Keep only Hebrew letters
        clean_word = re.sub(r'[^\u0590-\u05FF]', '', word)
        if clean_word:
            # Reverse it (PDFs often store Hebrew backwards)
            reversed_word = reverse_hebrew(clean_word)
            if is_valid_word(reversed_word):
                clean_words.append(reversed_word)

    # Logic: After removing all clubs/cities/headers, 
    # the names are usually the LAST two items remaining in the list 
    # (because the structure is usually: [Rank] [Name] [Family] [Club] [Time])
    # If we delete [Club], we are left with [Name] [Family].
    
    if len(clean_words) >= 2:
        # We take the last two valid words.
        # Usually one is first name, one is last name.
        # e.g., ['David', 'Cohen']
        first = clean_words[-1]
        last = clean_words[-2]
        
        # Filter single letter errors (like middle initials)
        if len(first) > 1 and len(last) > 1:
            return f"{last} {first}" # Returns "Cohen David"
            
    return None

def main():
    all_swimmers = set()
    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    print(f"🏊 Starting Optimized Scan on {len(files)} files...")

    for filename in files:
        path = os.path.join(PDF_FOLDER, filename)
        
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                        
                    lines = text.split('\n')
                    for line in lines:
                        # Only look at lines with a time or year (to skip text paragraphs)
                        if re.search(r'\d{2}:\d{2}', line) or re.search(r'20\d{2}', line) or re.search(r'19\d{2}', line):
                            name = parse_line(line)
                            if name:
                                all_swimmers.add(name)
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")

    # Create DataFrame
    df = pd.DataFrame(sorted(list(all_swimmers)), columns=['Name'])
    
    # Final cleanup: Remove names that look too short or identical (e.g. "Cohen Cohen")
    df = df[df['Name'].str.len() > 4]
    
    print(f"\n🎉 Success! Found {len(df)} unique swimmers.")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"💾 Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()