# 🔄 Google Drive to GitHub Notebook Sync Guide

## ⚠️ The Problem (What Went Wrong)

Your original sync script uploaded **empty notebooks** because:
```python
request = drive.files().get(fileId=f["id"], alt='media')  # ❌ Gets metadata, not notebook content
fh = BytesIO()
downloader = MediaIoBaseDownload(fh, request)  # ❌ Downloads empty data
```

Result: All 77 notebooks now contain only `{"cells": []}`

---

## ✅ The Solution (New Improved Script)

The `COLAB_SYNC_IMPROVED.py` script uses:
```python
request = drive_service.files().export_media(
    fileId=file_id,
    mimeType='application/ipynb'  # ✅ Exports full notebook format
)
```

This properly downloads the **complete notebook with all cells and metadata**.

---

## 🚀 How to Use the Improved Script

### Step 1: Get Your GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `ColabSync`
4. Select scopes: ✓ `repo` (full control of private repositories)
5. Click **"Generate token"** and **copy it immediately** (you won't see it again!)

### Step 2: Get Your Google Drive Folder ID
1. Open Google Drive
2. Navigate to your folder with notebooks (e.g., `ML_MTECH`)
3. Look at the URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID_HERE`
4. Copy the `YOUR_FOLDER_ID_HERE` part

### Step 3: Update the Script Configuration
In the `COLAB_SYNC_IMPROVED.py` script, find and update:

```python
# GitHub Configuration
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxx"  # Paste your token here
OWNER = "Shrihariharan1999"
REPO = "Machine_Learning_MTECH"
BRANCH = "main"

# Google Drive Configuration
DRIVE_FOLDER_ID = "1234567890abcdef"  # Paste your folder ID here
```

### Step 4: Run in Google Colab
1. Open a new cell in Google Colab
2. Copy **ALL** the code from `COLAB_SYNC_IMPROVED.py`
3. Paste it into the Colab cell
4. Run the cell

The script will:
- ✓ Scan your Google Drive folder
- ✓ Download all `.ipynb` files with full content
- ✓ Preserve folder structure on GitHub
- ✓ Update existing notebooks or create new ones
- ✓ Show progress and summary

---

## 📊 Expected Output

```
======================================================================
GOOGLE DRIVE TO GITHUB NOTEBOOK SYNC
======================================================================

1. Authenticating with Google Drive...
✓ Authenticated

2. Scanning Google Drive folder (ID: 1Dpf2QsEY93uDiYxquIM...)...
✓ Found 77 notebook(s)

3. Syncing notebooks to GitHub...
----------------------------------------------------------------------

Processing: 01_Fundamentals/pythonbasics.ipynb
  Downloading from Drive... ✓
  Uploading to GitHub... ✓ Created

Processing: 02_Supervised_Learning/Linear Regression.ipynb
  Downloading from Drive... ✓
  Uploading to GitHub... ✓ Updated

... (more notebooks)

======================================================================
SYNC COMPLETE - SUMMARY
======================================================================
✓ Uploaded:  45
✓ Updated:   32
⚠ Skipped:   0
❌ Failed:   0
Total:       77
======================================================================

✅ All notebooks synced successfully!
```

---

## 🔍 Troubleshooting

### Problem: "Invalid credentials"
**Solution:** Make sure your GitHub token is correct and has not expired

### Problem: "Folder not found"
**Solution:** Double-check your `DRIVE_FOLDER_ID` is correct

### Problem: "notebooks missing 'cells' key"
**Solution:** Some notebooks might genuinely be empty in Colab. These will be skipped.

### Problem: "401 Unauthorized on GitHub"
**Solution:** Your token expired or is wrong. Generate a new one.

---

## 🛠️ Key Improvements Over Original Script

| Feature | Original ❌ | Improved ✅ |
|---------|-----------|-----------|
| Notebook Format | `get_media` (metadata only) | `export_media` (full notebook) |
| Content Downloaded | ❌ Empty | ✅ Complete with cells |
| Folder Structure | ❌ Flattened | ✅ Preserved |
| Duplicate Handling | ❌ Not handled | ✅ Automatically updates |
| Error Handling | ❌ Minimal | ✅ Comprehensive |
| Validation | ❌ None | ✅ Checks for valid JSON |
| Progress Tracking | ❌ Minimal | ✅ Detailed logging |

---

## 📝 Next Steps

1. **Fix the Current Notebooks:**
   - Use this script to re-sync from Google Drive
   - This will overwrite the empty notebooks with actual content

2. **Prevent This in Future:**
   - Always use `export_media` with `mimeType='application/ipynb'`
   - Test with a few notebooks first before syncing all
   - Verify a sample after upload: visit https://github.com/Shrihariharan1999/Machine_Learning_MTECH/blob/main/01_Fundamentals/pythonbasics.ipynb and check if it has content

3. **Alternative: Manual Sync**
   - If you prefer not to use scripts, download `.ipynb` files from Colab manually
   - File → Download → Download .ipynb
   - Push to GitHub using `git add` and `git commit`

---

## ⚙️ Advanced Usage

### Sync Only Specific Folder
Modify the script to use a specific subfolder ID instead of the main folder.

### Sync on a Schedule
Set up a Google Cloud Function or GitHub Actions to run this periodically.

### Dry Run (Preview What Will Sync)
Add this flag to preview without uploading:
```python
DRY_RUN = True  # Won't actually upload
```

---

## 🔐 Security Note

- Never commit your `GITHUB_TOKEN` to GitHub
- The token gives full access to your repositories
- Consider using a separate "bot" account for automation
- Regularly rotate your tokens

---

**Created:** July 2026  
**Script Version:** 2.0 (Fixed Export)  
**Status:** ✅ Ready to use
