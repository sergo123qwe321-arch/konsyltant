import os
import sys

FORBIDDEN_FILES = {"процесс.txt", "процесс для гемини.txt", "log.txt", "history.txt"}

def check_no_txt_logs():
    found = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for f in files:
            lower = f.lower()
            if lower in FORBIDDEN_FILES or (lower.endswith(".txt") and "процесс" in lower):
                found.append(os.path.join(root, f))
    if found:
        print("ERROR: Forbidden log files found in repository! Use process.md instead:")
        for path in found:
            print(f"  - {path}")
        sys.exit(1)
    print("OK: No forbidden txt log files found. Single source of truth is process.md.")

if __name__ == "__main__":
    check_no_txt_logs()
