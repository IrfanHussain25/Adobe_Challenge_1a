# 🧾 Adobe India Hackathon 2025 (Challenge 1A) - Team Syn3rgy

## 🚀 Overview

This is a Dockerized solution for **Challenge 1A** of the Adobe India Hackathon 2025. The goal is to extract structured data (titles and headings) from PDF documents and output it in a well-formed JSON format. The system is designed for offline CPU execution, handles both simple and complex PDFs, and adheres to strict performance and resource constraints.

---

## 🧠 Approach

The solution processes all PDFs placed in the `/app/input` directory (read-only mount) and generates corresponding `.json` files in `/app/output`. Each JSON contains:
- The document **title** (detected using font size and layout),
- A hierarchical **outline** of headings (`H1`, `H2`, `H3`), extracted using:
  - **Regex-based numbered pattern matching**
  - **Font size heuristics with aggressive visual filters** to exclude logos, labels, and noise

No machine learning models are used, ensuring fast startup, low resource usage, and compatibility across environments.

---

## 📦 Dependencies Used

All dependencies are either part of Python’s standard library or installable via PyPI:

| Library   | Purpose                            |
|-----------|------------------------------------|
| `PyMuPDF` | PDF parsing, layout and font info  |
| `re`      | Regex-based heading detection      |
| `json`    | JSON serialization                 |
| `pathlib` | Cross-platform file handling       |
| `collections` | Frequency counting for font sizes |

---

## 🛠️ How to Build & Run

### 🐳 Build the Docker Image

```bash
docker build --platform linux/amd64 -t round-1a .
```

### ▶️ Run the Container

```bash
docker run --rm \
  -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
  -v "$(pwd)/sample_dataset/outputs:/app/output" \
  --network none \
  round-1a
```

## 📂 Project Structure
```
ADOBE_CHALLENGE_1A/
├── Dockerfile
├── process_pdfs.py              # Main processing script
├── sample_dataset/
│   ├── pdfs/                    # Input PDFs (read-only mount)
│   ├── output/                  # Output JSONs (written here)
│   └── schema/
│       └── output_schema.json   # JSON schema for validation
└── README.md                    # You're reading it
```

## 📤 Output Format
Each PDF is converted into a .json file:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section Heading",
      "page": 0
    },
    
  ]
}
```


## 👨‍💻 Developed By
### Team Syn3rgy
### Submission for Adobe India Hackathon 2025

