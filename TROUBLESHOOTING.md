# 🔧 Troubleshooting Corrupted Notebooks

## Issue: Notebooks Show as Empty in GitHub

If you see notebooks on GitHub but they're empty (showing "Notebook could not be converted from version 1 to version 2"), follow this guide.

---

## ✅ Diagnostic Checklist

- [ ] Check file size: `Get-ChildItem *.ipynb | Select-Object Name, Length`
  - Should be > 1KB for real notebooks
  - If < 100 bytes: notebook is corrupted

- [ ] Check content structure using PowerShell:
```powershell
$content = Get-Content "notebook.ipynb" -Raw
$json = $content | ConvertFrom-Json
if ($json.cells) { Write-Host "✓ Has cells" } else { Write-Host "✗ Missing cells" }
```

- [ ] Verify GitHub view:
  - Go to: https://github.com/Shrihariharan1999/Machine_Learning_MTECH
  - Click a notebook → Preview
  - If blank: notebook is empty on GitHub

---

## 🔴 Current Status (July 2026)

**ISSUE IDENTIFIED:** All 77 notebooks are corrupted
- All files contain only: `{"cells": []}`
- Missing: metadata, nbformat, actual code/markdown

**ROOT CAUSE:** Colab sync script used incorrect export method
```python
# ❌ WRONG - Downloads metadata only
request = drive.files().get(fileId=f["id"], alt='media')

# ✅ CORRECT - Downloads full notebook
request = drive_service.files().export_media(
    fileId=file_id,
    mimeType='application/ipynb'
)
```

---

## 🚀 Recovery Steps

### Option 1: Use Improved Sync Script (RECOMMENDED)
1. Open `COLAB_SYNC_IMPROVED.py`
2. Follow instructions in `SYNC_SETUP_GUIDE.md`
3. Run the script in Google Colab
4. Commits will be automatically pushed to GitHub

**Time:** ~5-10 minutes for all notebooks

### Option 2: Manual Re-download
1. Go to Google Colab
2. For each notebook:
   - Open it
   - File → Download → Download .ipynb
   - Organize into correct folder locally
3. Commit and push:
```bash
git add -A
git commit -m "Fix: Replace corrupted notebooks with complete versions"
git push origin main
```

**Time:** Longer (1 notebook per 1-2 minutes)

### Option 3: Restore from Backup
If you have backups of your notebooks:
1. Copy backup files to correct folders
2. Commit and push

---

## 📋 Validation After Fix

After syncing, verify notebooks are fixed:

```bash
# Check file sizes (should be > 1KB each)
Get-ChildItem -Recurse -Filter "*.ipynb" | Where-Object {$_.Length -gt 1000} | Measure-Object

# Check a specific notebook
$nb = Get-Content "01_Fundamentals/pythonbasics.ipynb" -Raw
$json = $nb | ConvertFrom-Json
if ($json.cells.Count -gt 0) { Write-Host "✓ Fixed!" } else { Write-Host "✗ Still empty" }
```

---

## 📊 Before & After

### BEFORE (Corrupted)
```json
{
    "cells": []
}
```
- File size: ~18 bytes
- Issue: No content

### AFTER (Fixed)
```json
{
    "cells": [
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "import pandas as pd"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {...},
        "language_info": {...}
    },
    "nbformat": 4,
    "nbformat_minor": 2
}
```
- File size: 5-100+ KB
- Issue: ✓ Fixed

---

## 🔗 Related Files

- [`COLAB_SYNC_IMPROVED.py`](COLAB_SYNC_IMPROVED.py) - Fixed sync script
- [`SYNC_SETUP_GUIDE.md`](SYNC_SETUP_GUIDE.md) - Detailed setup instructions
- [`README.md`](README.md) - Main repository documentation

---

## 💡 Prevention Tips

For future syncs:
1. ✅ Always use `export_media` with `mimeType='application/ipynb'`
2. ✅ Validate JSON structure after download
3. ✅ Test with 1-2 notebooks first
4. ✅ Keep backup of your notebooks in Google Drive
5. ✅ Document your sync process

---

## 📞 Need Help?

If notebooks still show as empty after following these steps:
1. Check the sync script output for errors
2. Verify GitHub token permissions
3. Try syncing just 1 notebook first
4. Check that Google Drive folder structure is organized

---

**Last Updated:** July 21, 2026  
**Status:** 🔴 Awaiting fix - Ready to proceed with improved script
