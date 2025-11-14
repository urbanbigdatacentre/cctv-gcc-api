from pathlib import Path

def get_md_description(of: str):
    docs_path = Path(__file__).parent / "docs"
    md_path = docs_path / f"{of}.md" 

    return md_path.read_text()