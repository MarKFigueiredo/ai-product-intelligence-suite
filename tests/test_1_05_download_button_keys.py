from pathlib import Path


def _download_button_blocks(text: str):
    marker = "st.download_button("
    idx = 0
    while True:
        start = text.find(marker, idx)
        if start == -1:
            return
        pos = start + len(marker)
        depth = 1
        in_string = None
        escape = False
        while pos < len(text) and depth:
            ch = text[pos]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == in_string:
                    in_string = None
            else:
                if ch in {'"', "'"}:
                    in_string = ch
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            pos += 1
        yield text[start:pos]
        idx = pos


def test_all_streamlit_download_buttons_have_explicit_keys():
    files = list(Path('.').rglob('*.py'))
    failures = []
    for path in files:
        if any(part in {'.venv', '.git', '__pycache__'} for part in path.parts):
            continue
        text = path.read_text(encoding='utf-8')
        for block in _download_button_blocks(text):
            if 'key=' not in block:
                failures.append(f"{path}: {block[:120]}")
    assert not failures, "download_button calls without explicit key:\n" + "\n".join(failures)
