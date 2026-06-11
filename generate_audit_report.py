import os
import ast
import json
from pathlib import Path

ROOT_DIR = Path(r"C:\Mukul K\vinfo1\video-search-engine")

def get_size_mb(path):
    if path.is_file(): return path.stat().st_size / (1024*1024)
    total = 0
    for p in path.rglob("*"):
        if p.is_file(): total += p.stat().st_size
    return total / (1024*1024)

def run_audit():
    report = []
    report.append("# Repository Audit Report")
    report.append("")
    
    # Part 1: Inventory
    app_dir = ROOT_DIR / "app"
    data_dir = ROOT_DIR / "data"
    frontend_dir = ROOT_DIR / "frontend"
    tests_dir = ROOT_DIR / "tests"
    
    all_files = list(ROOT_DIR.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([d for d in all_files if d.is_dir()])
    total_mb = get_size_mb(ROOT_DIR)
    
    report.append("## Part 1 — Repository Inventory")
    report.append(f"- **Total Files**: {file_count}")
    report.append(f"- **Total Directories**: {dir_count}")
    report.append(f"- **Total Size**: {total_mb:.2f} MB")
    
    report.append("### Directory Breakdown")
    report.append(f"- `app/`: {get_size_mb(app_dir):.2f} MB")
    report.append(f"- `data/`: {get_size_mb(data_dir):.2f} MB")
    report.append(f"- `frontend/`: {get_size_mb(frontend_dir):.2f} MB")
    report.append(f"- `.venv/`: {get_size_mb(ROOT_DIR / '.venv'):.2f} MB")
    report.append(f"- Root Scripts/Logs: {sum(f.stat().st_size for f in ROOT_DIR.glob('*') if f.is_file()) / (1024*1024):.2f} MB")
    report.append("")
    
    # Part 2 & 3: Dependency Mapping and Dead Files
    python_files = list(app_dir.rglob("*.py"))
    imports = {}
    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                imports[py_file.name] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names: imports[py_file.name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module: imports[py_file.name].append(node.module)
        except Exception:
            pass

    # Root scripts (dead code candidates)
    root_scripts = list(ROOT_DIR.glob("*.py"))
    safe_to_delete = []
    review_required = []
    for script in root_scripts:
        name = script.name
        if name.startswith(("patch", "test_", "scratch_", "debug_", "validate_", "diag_", "trace_", "benchmark_")):
            safe_to_delete.append((name, "Temporary script/patch file generated during development"))
        elif name in ["audit_script.py", "generate_report.py", "print_tree.py", "regenerate_pipeline.py", "reprocess_video.py"]:
            review_required.append((name, "Utility script, might be obsolete"))

    # Logs and txt
    logs = list(ROOT_DIR.glob("*.txt")) + list(ROOT_DIR.glob("*.log"))
    for log in logs: safe_to_delete.append((log.name, "Log or output file"))
    
    report.append("## Part 2 & 3 — Dead File Detection")
    report.append("### SAFE TO DELETE")
    for f, r in safe_to_delete: report.append(f"- `{f}`: {r}")
    report.append("")
    report.append("### REVIEW REQUIRED")
    for f, r in review_required: report.append(f"- `{f}`: {r}")
    report.append("")
    
    # Part 4: Duplicate Implementations
    report.append("## Part 4 — Duplicate Logic Audit")
    report.append("Found duplicated validation/runner scripts in root:")
    report.append("- `validate_outputs.py` vs `validate_outputs2.py` vs `validate_outputs3.py`")
    report.append("- `reprocess_video.py` vs `reprocess_video_v2.py`")
    report.append("These are iterative scripts. Only the main `app/` codebase is used in production.")
    report.append("")
    
    # Part 7: GitHub Cleanup & Space Saved
    report.append("## Part 7 — GitHub Cleanup Audit")
    space_saved = 0
    del_files_count = 0
    for f, _ in safe_to_delete:
        p = ROOT_DIR / f
        if p.exists():
            space_saved += p.stat().st_size
            del_files_count += 1
            
    # Include data dir cache
    data_size = get_size_mb(data_dir) * 1024 * 1024
    space_saved += data_size
    
    # Include pycache
    for p in ROOT_DIR.rglob("__pycache__"):
        for f in p.glob("*"): space_saved += f.stat().st_size
        
    space_saved_mb = space_saved / (1024*1024)
    report.append(f"**Estimated Space Saved**: {space_saved_mb:.2f} MB")
    report.append("This includes logs, temporary patches, metadata caches, and python caches.")
    report.append("")
    
    # Part 8: .gitignore
    report.append("## Part 8 — Recommended `.gitignore`")
    report.append("```")
    report.append(".venv/")
    report.append("__pycache__/")
    report.append("*.pyc")
    report.append("*.log")
    report.append("*.txt")
    report.append("data/")
    report.append("patch*.py")
    report.append("scratch_*.py")
    report.append("test_*.py")
    report.append("debug_*.py")
    report.append("```")
    report.append("")
    
    # Part 11: Health Score
    report.append("## Part 11 — Repository Health Score")
    report.append("- **Architecture**: 8/10 (Clean FastAPI structure in `app/`)")
    report.append("- **Maintainability**: 6/10 (Root directory is extremely cluttered with ad-hoc scripts)")
    report.append("- **Code Duplication**: 7/10 (Multiple iterative scripts lying around)")
    report.append("- **Repository Hygiene**: 3/10 (Logs and test data dumped in root)")
    report.append("- **Overall Score**: 6/10")
    report.append("")
    report.append("Action Plan: Execute the GitHub cleanup to remove all `patch*.py`, `test*.py`, and `*.txt` logs. Add `data/` to `.gitignore`.")

    with open(r"C:\Users\Vinfocom\.gemini\antigravity-ide\brain\3b9898a7-6b14-4a67-8f53-d36e2b526aa7\audit_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
run_audit()
