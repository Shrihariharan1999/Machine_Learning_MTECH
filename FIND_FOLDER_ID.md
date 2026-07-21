# 📁 How to Find Your Google Drive Folder ID

## Step-by-Step Guide

### Step 1: Open Google Drive
Go to: https://drive.google.com

### Step 2: Navigate to Your ML Notebooks Folder
Find the folder containing your Jupyter notebooks. Examples:
- `ML_MTECH`
- `Machine_Learning_MTECH`
- `MTech_Projects`
- Or whatever you named it

**Click to open the folder**

### Step 3: Look at the URL in Your Browser

The URL will look like this:
```
https://drive.google.com/drive/folders/FOLDER_ID_HERE
```

**Example:**
```
https://drive.google.com/drive/folders/1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ
```

### Step 4: Copy the Folder ID

The folder ID is the long string between `/folders/` and the end of URL.

**In the example above:**
- Full URL: `https://drive.google.com/drive/folders/1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ`
- Folder ID: `1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ`

---

## Visual Example

```
https://drive.google.com/drive/folders/1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ
                                       ↑
                            COPY THIS PART
                            (25-33 characters)
```

---

## What to Do Next

1. **Copy your folder ID** (the long string)
2. **Open the sync script** in Google Colab
3. **Find this line:**
   ```python
   DRIVE_FOLDER_ID = "your_google_drive_folder_id"
   ```
4. **Replace with your ID:**
   ```python
   DRIVE_FOLDER_ID = "1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ"
   ```
5. **Also update GitHub token:**
   ```python
   GITHUB_TOKEN = "ghp_your_actual_token_here"
   ```
6. **Run the script!**

---

## Quick Checklist

- [ ] I found my ML notebooks folder in Google Drive
- [ ] I opened the folder
- [ ] I copied the folder ID from the URL
- [ ] I updated `DRIVE_FOLDER_ID` in the script
- [ ] I updated `GITHUB_TOKEN` in the script
- [ ] I'm ready to run the sync script in Colab

---

## Troubleshooting

### "I can't find my notebooks folder"
- Check your Google Drive home: https://drive.google.com
- Look in "My Drive" and "Shared with me"
- Use the search icon to find it by name

### "The folder ID is too short"
- Make sure you copied the ENTIRE ID
- It should be 25-33 characters long
- Don't include the `/folders/` part

### "I don't see `/folders/` in the URL"
- Make sure you clicked to **open the folder**
- If you only selected it, the URL won't show the folder ID
- Try clicking into it

---

## Alternative: Using a Specific Folder

If your notebooks are organized in Google Drive like this:
```
ML_MTECH/
├── 01_Fundamentals/
├── 02_Supervised_Learning/
├── 03_Unsupervised_Learning/
└── ... (other folders)
```

**Use the ID of the `ML_MTECH` folder** (the parent folder containing all your notebooks)

The sync script will automatically detect all subfolders and maintain the structure on GitHub.

---

**Created:** July 2026  
**Purpose:** Help you find your Google Drive folder ID for the sync script
