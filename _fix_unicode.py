"""Fix Unicode characters in Python files (GBK compat for Windows)"""
import os
from pathlib import Path

base = Path(r"C:\Users\A\.openclaw\workspace\月产品")
fixes = {
    "\u2713": "",   # checkmark
    "\u2022": "*",      # bullet
    "\u25b8": ">",      # triangle right
    "\u25e2": ".",      # small triangle
    "\u25e3": ".",      # small triangle
    "\u25e4": ".",      # small triangle
}

for pyfile in base.rglob("*.py"):
    content = pyfile.read_bytes()
    original = content
    try:
        text = content.decode("utf-8")
        for old, new in fixes.items():
            text = text.replace(old, new)
        
        # Also find any non-ASCII chars in print() strings
        lines = text.split("\n")
        fixed = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("print(") or stripped.startswith("f'") or stripped.startswith('f"'):
                # Find non-ASCII characters
                has_bad = any(ord(c) > 127 for c in line)
                if has_bad:
                    # Replace non-ASCII chars in string literals only
                    new_line = ""
                    for c in line:
                        if ord(c) > 127:
                            new_line += "?"
                            fixed = True
                        else:
                            new_line += c
                    lines[i] = new_line
        
        if fixed:
            text = "\n".join(lines)
        
        new_bytes = text.encode("utf-8")
        if new_bytes != original:
            pyfile.write_bytes(new_bytes)
            print(f"Fixed: {pyfile.name}")
    except Exception as e:
        print(f"Error {pyfile.name}: {e}")

print("Done.")

