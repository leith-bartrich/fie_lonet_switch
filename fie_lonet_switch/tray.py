import sys

def main():
    print("The FIE Lonet Switch tray application is only available on macOS.", file=sys.stderr)
    # Or, alternatively, use a logger if the project has one configured.
    # Or, do nothing silently. For now, a print statement is fine.

if __name__ == "__main__":
    # This part is optional, as tray_entry.py calls tray.main() directly.
    # However, it's good practice to include it.
    main()
