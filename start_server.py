print("Step 1: Imports starting...", flush=True)
import sys
import os
print("Step 2: Sys/os imported", flush=True)
import uvicorn
print("Step 3: Uvicorn imported", flush=True)
try:
    print("Step 4: Importing app.main...", flush=True)
    from app.main import app
    print("Step 5: App main imported successfully", flush=True)
except BaseException as e:
    print(f"Import BaseException: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("Step 6: Starting uvicorn.run...", flush=True)
try:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="debug")
    print("Step 7: uvicorn.run completed normally", flush=True)
except BaseException as e:
    print(f"Run BaseException: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
