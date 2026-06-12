import sys
import traceback
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.main import app
    with open("main_import_success.txt", "w") as f:
        f.write("Imported app successfully!\n")
except Exception as e:
    with open("main_import_error.txt", "w") as f:
        f.write(f"Exception: {type(e).__name__}\n")
        f.write(f"Message: {e}\n")
        traceback.print_exc(file=f)
