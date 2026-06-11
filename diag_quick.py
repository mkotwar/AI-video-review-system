"""Quick diagnostic - writes all output to diag_results.txt"""
import subprocess, json, os, sys, time

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag_results.txt")
lines = []

def log(msg):
    lines.append(str(msg))
    print(msg)

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return (r.stdout.strip() + "\n" + r.stderr.strip()).strip()
    except Exception as e:
        return f"ERROR: {e}"

log("=" * 60)
log("  QUICK VLM DIAGNOSTIC")
log(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 60)

# GPU
log("\n=== GPU INFO ===")
log(run('"C:\\WINDOWS\\system32\\nvidia-smi.exe"'))
log("\n=== GPU CSV ===")
log(run('"C:\\WINDOWS\\system32\\nvidia-smi.exe" --query-gpu=name,memory.total,memory.used,memory.free,driver_version,pstate,clocks.current.graphics,clocks.current.memory,power.draw,power.limit,compute_mode --format=csv'))

# CUDA via PyTorch
log("\n=== PYTORCH CUDA ===")
try:
    import torch
    log(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log(f"Device: {torch.cuda.get_device_name(0)}")
        log(f"CUDA version: {torch.version.cuda}")
        props = torch.cuda.get_device_properties(0)
        log(f"VRAM: {props.total_mem / (1024**3):.2f} GB")
    else:
        log("NO GPU AVAILABLE TO PYTORCH")
except Exception as e:
    log(f"PyTorch error: {e}")

# Ollama
log("\n=== OLLAMA ===")
log(f"ollama version: {run('ollama --version')}")
log(f"\nollama list:\n{run('ollama list')}")
log(f"\nollama ps:\n{run('ollama ps')}")

# Check if Ollama server is running
log("\n=== OLLAMA SERVER CHECK ===")
try:
    import httpx
    resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
    log(f"Ollama API status: {resp.status_code}")
    log(f"Models: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    log(f"Ollama API UNREACHABLE: {e}")

# Check ollama config env vars
log("\n=== OLLAMA ENV VARS ===")
for v in ["OLLAMA_NUM_PARALLEL", "OLLAMA_MAX_LOADED_MODELS", "OLLAMA_HOST",
           "OLLAMA_GPU_OVERHEAD", "OLLAMA_MAX_QUEUE", "OLLAMA_NUM_GPU",
           "OLLAMA_FLASH_ATTENTION", "OLLAMA_KV_CACHE_TYPE", "OLLAMA_CONTEXT_LENGTH"]:
    log(f"  {v}: {os.environ.get(v, 'NOT SET')}")

# GPU Processes
log("\n=== GPU PROCESSES ===")
log(run('"C:\\WINDOWS\\system32\\nvidia-smi.exe" --query-compute-apps=pid,process_name,used_gpu_memory --format=csv'))

# .env config
log("\n=== .ENV CONFIG ===")
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        log(f.read())

# System RAM
log("\n=== SYSTEM MEMORY ===")
try:
    import psutil
    mem = psutil.virtual_memory()
    log(f"Total RAM: {mem.total / (1024**3):.1f} GB")
    log(f"Available: {mem.available / (1024**3):.1f} GB")
    log(f"Used: {mem.used / (1024**3):.1f} GB ({mem.percent}%)")
except ImportError:
    log("psutil not available")

# Write results
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

log(f"\nResults written to: {OUT}")
