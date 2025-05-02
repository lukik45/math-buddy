import pandas as pd
import re
import json

# Roman to integer conversion
def roman_to_int(roman):
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev_value = 0
    for char in reversed(roman):
        value = roman_map.get(char, 0)
        if value < prev_value:
            result -= value
        else:
            result += value
            prev_value = value
    return result

# document = 'realizacja_podstawy_4_6'
document = 'realizacja_podstawy_7_8'

# Load and clean the CSV
file_path = f"../data/03_extracted_csvs/{document}.csv"
df = pd.read_csv(file_path, sep=';')
df.columns = [col.strip().replace('\n', ' ').replace('\t', '').strip() for col in df.columns]
df = df.applymap(lambda x: x.strip().replace('\n', ' ').replace('\t', '') if isinstance(x, str) else x)
df.dropna(how='all', inplace=True)
df.reset_index(drop=True, inplace=True)

# Identify chapter rows using Roman numeral and dot (e.g. I.)
chapter_pattern = re.compile(r'^([IVXLCDM]+)\.\s+(.*)$')  # Matches "I. Name"

chapters = []
current_chapter = None

for _, row in df.iterrows():
    content = row.iloc[0]
    if pd.isna(content):
        continue

    content = re.sub(r'\s{2,}', ' ', content.strip())

    # Check if this row is a chapter
    chapter_match = chapter_pattern.match(content)
    if chapter_match:
        chapter_roman = chapter_match.group(1)
        chapter_name = chapter_match.group(0)  # Full "I. Name..."
        chapter_number = roman_to_int(chapter_roman)

        current_chapter = {
            "level": "7-8",
            "number": chapter_number,  # now as integer
            "name": chapter_name,
            "requirements": []
        }
        chapters.append(current_chapter)
        continue

    if current_chapter and content:
        # Try to extract requirement number (e.g. "1)", "3.", etc.)
        req_match = re.match(r'^(\d+)[\)\.]?\s*(.*)', content)
        if req_match:
            requirement_number = int(req_match.group(1))
            requirement_name = req_match.group(2)
        else:
            requirement_number = None
            requirement_name = content

        current_chapter["requirements"].append({
            "number": requirement_number,
            "name": requirement_name
        })

# Save to JSON
output_path = f'../data/04_processed_data/{document}.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)

print(f"JSON saved as {output_path} ✅")
