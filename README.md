# FileScanner CLI

A dependency-free Python command-line tool that inventories files and can identify
byte-for-byte duplicates without modifying the scanned directory.

```powershell
python cli.py --scan .
python cli.py --scan . --find-duplicates --filter-ext .py,.md
python cli.py --scan . --output results.json
```

Run the tests with `python -m pytest`.
