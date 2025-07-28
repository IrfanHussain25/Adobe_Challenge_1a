import os
import re
import json
from pathlib import Path
from collections import Counter
import fitz  # PyMuPDF


def get_common_text_style(page):
    styles = Counter()
    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                if "spans" in line:
                    for span in line["spans"]:
                        if span['size'] > 6:
                            styles[round(span['size'])] += 1
    return styles.most_common(1)[0][0] if styles else 12.0


def extract_title(doc):
    if doc.page_count == 0:
        return ""

    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]
    max_font_size = 0
    title_candidates = []

    def is_junk(text):
        return re.fullmatch(r'[\W_]+', text.strip()) is not None

    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if span['size'] > max_font_size and not is_junk(span['text']):
                        max_font_size = span['size']

    if max_font_size == 0:
        return ""

    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                if "spans" in line and line["spans"]:
                    avg_size = sum(s['size'] for s in line['spans']) / len(line['spans'])
                    if abs(avg_size - max_font_size) < 1:
                        line_text = "".join(s['text'] for s in line['spans']).strip()
                        if line_text and not is_junk(line_text):
                            title_candidates.append({'text': line_text, 'y0': line['bbox'][1]})

    if not title_candidates:
        return ""

    title_candidates.sort(key=lambda item: item['y0'])
    title_lines = [title_candidates[0]['text']]
    for i in range(1, len(title_candidates)):
        if abs(title_candidates[i]['y0'] - title_candidates[i - 1]['y0']) < max_font_size * 2:
            title_lines.append(title_candidates[i]['text'])
        else:
            break

    return " ".join(title_lines)


def extract_headings(doc):
    outline = []
    if doc.page_count < 1:
        return outline

    body_size = get_common_text_style(doc[0])

    heading_patterns = [
        (re.compile(r"^\d{1,2}\.\d{1,2}\.\d{1,2}\.?\s+"), "H3"),
        (re.compile(r"^\d{1,2}\.\d{1,2}\.?\s+"), "H2"),
        (re.compile(r"^\d{1,2}\.?\s+"), "H1"),
        (re.compile(r"^[A-Z]\.\s+"), "H2"),
    ]

    for page_num, page in enumerate(doc):
        table_bboxes = [t.bbox for t in page.find_tables()]
        for block in page.get_text("dict", sort=True)["blocks"]:
            block_bbox = fitz.Rect(block['bbox'])
            if any(block_bbox.intersects(table_bbox) for table_bbox in table_bboxes):
                continue

            for line in block.get("lines", []):
                if not line.get("spans"):
                    continue
                text = "".join(s['text'] for s in line['spans']).strip()
                if not text or len(text) < 3:
                    continue

                is_heading_found = False
                for pattern, level in heading_patterns:
                    if pattern.match(text):
                        clean_text = re.sub(pattern, '', text, 1).strip()
                        if clean_text and len(clean_text.split()) < 20:
                            outline.append({"level": level, "text": clean_text, "page": page_num})
                            is_heading_found = True
                            break
                if is_heading_found:
                    continue

                span = line['spans'][0]
                if span['size'] > body_size + 3:
                    word_count = len(text.split())
                    if 1 < word_count < 10:
                        if ':' in text or 'www.' in text.lower() or '.com' in text.lower():
                            continue
                        if text.isupper() and any(char.isdigit() for char in text):
                            continue
                        if ' ' not in text:
                            continue
                        if re.fullmatch(r'[\W_]+', text.strip()):
                            continue
                        outline.append({"level": "H1", "text": text, "page": page_num})

    return outline


def process_single_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None

    title = extract_title(doc)
    outline = extract_headings(doc)
    doc.close()

    if title:
        title_clean = title.strip().lower()
        outline = [h for h in outline if h['text'].strip().lower() != title_clean]

    return {"title": title.strip(), "outline": outline}


def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in /app/input")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process...")
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        structured_data = process_single_pdf(pdf_file)
        if structured_data:
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=4, ensure_ascii=False)
            print(f"Successfully generated {output_file.name}")


if __name__ == "__main__":
    main()
