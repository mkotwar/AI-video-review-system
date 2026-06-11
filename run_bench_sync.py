import subprocess

def run_benchmark():
    result = subprocess.run([r"c:\Mukul K\vinfo1\video-search-engine\.venv\Scripts\python.exe", "benchmark_pipeline.py"], capture_output=True, text=True, cwd="c:/Mukul K/vinfo1/video-search-engine")
    with open("c:/Mukul K/vinfo1/video-search-engine/benchmark_log.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write("\n---\n")
        f.write(result.stderr)

if __name__ == "__main__":
    run_benchmark()
