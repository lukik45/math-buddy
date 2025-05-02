import re
import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz

# Get the directory where the script is located
BASE_DIR = Path(__file__).resolve().parent

# Define input/output directories relative to the script
EXTRACTED_DIR = BASE_DIR / ".." / "data" / "03_extracted_csvs"
OUTPUT_DIR = BASE_DIR / ".." / "data" / "04_processed_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Create if not exists

def clean_text(text):
    """Remove unnecessary characters and normalize spaces."""
    if isinstance(text, str):
        text = text.replace('*', '').replace('.', '').replace('\u00A0', ' ')
        return ' '.join(text.split())
    return text

def roman_to_int(roman):
    """Convert a Roman numeral to an integer."""
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

def extract_chapters_and_requirements(text):
    """
    Extract all chapter markers and requirement numbers from a skill string.
    Returns a list of tuples: (chapter_int, requirement_number)
    e.g. "VII. Proste i odcinki. Uczeń : 2) ...; 3) ...; VIII. Kąty. Uczeń : 4) ..." 
    returns [(7, 2), (7, 3), (8, 4)]
    """
    results = []
    if not isinstance(text, str):
        return results
    # Find all chapter markers (Roman numerals followed by a dot)
    chapter_pattern = re.compile(r'([IVXLCDM]+)\.')
    chapters = list(chapter_pattern.finditer(text))
    if not chapters:
        return results

    # Iterate over each chapter found
    for i, chap in enumerate(chapters):
        chapter_roman = chap.group(1)
        chapter_int = roman_to_int(chapter_roman)
        start = chap.end()
        # Determine region: from this chapter to the next, or end of text
        end = chapters[i+1].start() if i+1 < len(chapters) else len(text)
        chapter_text = text[start:end]
        # Find all requirement numbers within this chapter region (e.g., "2)" or "3)")
        req_numbers = re.findall(r'(\d+)\)', chapter_text)
        for num in req_numbers:
            results.append((chapter_int, int(num)))
    return results

def process_grade(grade):
    print(f"\n▶️ Processing grade {grade}...")

    # Define file paths using relative directories
    plan_file = EXTRACTED_DIR / f"plan_realizacji_{grade}.csv"
    base_file = EXTRACTED_DIR / f"rozklad_materialu_a_podstawa_{grade}.csv"
    output_file = OUTPUT_DIR / f"merged_grade_{grade}.csv"

    # === Load and clean plan (core curriculum: temat -- cele szczegółowe) ===
    df_plan = pd.read_csv(plan_file, sep=';')
    df_plan.columns = [col.strip().replace('\n', ' ').replace('\t', '').strip() for col in df_plan.columns]
    df_plan = df_plan.applymap(lambda x: ' '.join(str(x).replace('\n', ' ').replace('\t', '').split()) if isinstance(x, str) else x)
    df_plan.dropna(how='all', inplace=True)
    df_plan = df_plan.dropna(subset=["CELE PODSTAWOWE", "CELE PONADPODSTAWOWE"], how='all').fillna("")
    
    # Normalize both separators: · and \uf0b7
    def split_goals(text):
        if not isinstance(text, str):
            return []
        # Replace both variants with a common marker, then split
        normalized = text.replace('\uf0b7', '·')  # unify separators
        return [item.strip() for item in normalized.split('·') if item.strip()]

    # Create raw mapping
    raw_mapping = {
        row["Unnamed: 1"]: (row["CELE PODSTAWOWE"], row["CELE PONADPODSTAWOWE"])
        for _, row in df_plan.iterrows()
        if row["Unnamed: 1"] not in ("", "NaN")
    }

    # Process each row into structured format
    cele_data = []
    for temat, (cele_pod, cele_ponad) in raw_mapping.items():
        cele_pod_list = split_goals(cele_pod)
        cele_ponad_list = split_goals(cele_ponad)
        cele_data.append({
            "Temat": temat,
            "Cele podstawowe": cele_pod_list,
            "Cele ponadpodstawowe": cele_ponad_list
        })

    # Create final DataFrame
    df_cele = pd.DataFrame(cele_data)
    df_cele['temat_clean'] = df_cele['Temat'].apply(clean_text)


    # === Load and clean base curriculum (rozklad materialu: temat -- zagadnienia z podstawy programowej) ===
    df_base = pd.read_csv(base_file, sep=';')
    df_base.columns = [col.strip().replace('\n', ' ').replace('\t', '').strip() for col in df_base.columns]
    df_base = df_base.map(lambda x: ' '.join(str(x).replace('\n', ' ').replace('\t', '').split()) if isinstance(x, str) else x)
    df_base.dropna(how='all', inplace=True)
    df_base.columns = ['topic', 'skill']
    df_base.dropna(subset=['skill'], how='all', inplace=True)
    df_base['topic_clean'] = df_base['topic'].apply(clean_text)

    # === Fuzzy matching between topic (base) and Temat (plan) ===
    matches = df_base['topic_clean'].apply(
        lambda x: process.extractOne(x, df_cele['temat_clean'], scorer=fuzz.token_sort_ratio)
    )
    df_base['temat_clean_match'] = matches.apply(lambda x: x[0] if x else None)
    df_base['match_score'] = matches.apply(lambda x: x[1] if x else None)

    # === Merge the two datasets ===
    df_joined = df_base.merge(df_cele, left_on='temat_clean_match', right_on='temat_clean', how='outer')
    df_joined = df_joined[['Temat', 'topic', 'skill', 'match_score', 'Cele podstawowe', 'Cele ponadpodstawowe']]

    # === Extract chapter and requirement tuples from the skill column ===
    # Each cell in the new column "chapter_requirements" will contain a list of tuples, e.g. [(7,2), (7,3), (8,4)]
    df_joined['chapter_requirements'] = df_joined['skill'].apply(extract_chapters_and_requirements)

    # Save the merged DataFrame with the new extraction to CSV
    df_joined.to_csv(output_file, index=False)
    print(f"✅ Saved merged file for grade {grade} → {output_file}")

def main():
    # List the grades you want to process (as strings)
    grades_to_process = ['4','5','6', '7', '8']  # Change or extend this list as needed

    for grade in grades_to_process:
        process_grade(grade)

if __name__ == "__main__":
    main()
