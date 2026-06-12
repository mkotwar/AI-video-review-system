import os

def tail(filepath, n=100):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        return ''.join(lines[-n:])

with open(r"c:\Mukul K\vinfo1\video-search-engine\tail_out.txt", "w", encoding="utf-8") as out:
    try:
        out.write("--- APP.LOG ---\n")
        out.write(tail(r"c:\Mukul K\vinfo1\video-search-engine\data\logs\app.log", 200))
        out.write("\n\n--- ERRORS.LOG ---\n")
        out.write(tail(r"c:\Mukul K\vinfo1\video-search-engine\data\logs\errors.log", 200))
    except Exception as e:
        out.write(f"Failed: {e}")
