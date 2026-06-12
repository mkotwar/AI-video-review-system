import os

def grep_logs():
    log_file = r"c:\Mukul K\vinfo1\video-search-engine\data\logs\errors.log"
    if not os.path.exists(log_file):
        print("Log file not found!")
        return
        
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines[-1000:]):
        if "Exception" in line or "Traceback" in line or "Error" in line:
            print(line.strip())

if __name__ == "__main__":
    grep_logs()
