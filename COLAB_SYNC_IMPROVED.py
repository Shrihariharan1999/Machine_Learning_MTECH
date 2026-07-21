# ============================================================================
# IMPROVED GOOGLE DRIVE TO GITHUB SYNC SCRIPT FOR JUPYTER NOTEBOOKS
# ============================================================================
# This script properly downloads notebooks from Google Drive with all content
# and uploads them to GitHub while preserving folder structure.
# 
# Supports BOTH:
#   - Google Colaboratory notebooks (.ipynb files in Colab format)
#   - Regular .ipynb files (uploaded to Google Drive as regular files)
# 
# Usage: Run this in Google Colab
# ============================================================================

# QUICK START - 3 SIMPLE STEPS:
# ============================================================================
# 1. GET YOUR GITHUB TOKEN:
#    - Go to: https://github.com/settings/tokens
#    - Click "Generate new token" → "Generate new token (classic)"
#    - Select scope: ✓ repo
#    - Copy the token (you won't see it again!)
#    - Paste it below after "GITHUB_TOKEN = "
#
# 2. GET YOUR GOOGLE DRIVE FOLDER ID:
#    - Open Google Drive and navigate to your ML notebooks folder
#    - Look at the URL: https://drive.google.com/drive/folders/FOLDER_ID_HERE
#    - Copy the FOLDER_ID_HERE part
#    - Paste it below after "DRIVE_FOLDER_ID = "
#
# 3. RUN THIS SCRIPT IN COLAB:
#    - Copy ALL code below into a Colab cell
#    - Click "Run"
#    - Done!
# ============================================================================

import requests
import base64
from google.colab import drive
import os
import json
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# GitHub Configuration
GITHUB_TOKEN = "your_github_token_here"  # Get from: https://github.com/settings/tokens
OWNER = "Shrihariharan1999"
REPO = "Machine_Learning_MTECH"
BRANCH = "main"

# Google Drive Configuration
# Options:
#   1. Specific folder ID (25+ characters): "1Dpf2QsEY93uDiYxquIM3w13QkJmO7OPZ"
#   2. My Drive root: "root"
#   3. Leave as example and update before running
DRIVE_FOLDER_ID = "root"  # Use "root" for My Drive, or paste your folder ID here

# ============================================================================
# VALIDATION FUNCTION
# ============================================================================

def validate_configuration():
    """Validate that all configuration values have been updated"""
    print("Validating configuration...")
    print()
    
    errors = []
    
    # Check GitHub Token
    if GITHUB_TOKEN == "your_github_token_here":
        errors.append(
            "❌ GITHUB_TOKEN not configured\n"
            "   Get your token from: https://github.com/settings/tokens\n"
            "   Update line: GITHUB_TOKEN = 'your_actual_token_here'"
        )
    elif len(GITHUB_TOKEN) < 20:
        errors.append(
            "⚠ GITHUB_TOKEN seems too short\n"
            "   GitHub tokens are usually 40+ characters"
        )
    
    # Check Google Drive Folder ID
    if DRIVE_FOLDER_ID == "your_google_drive_folder_id":
        errors.append(
            "❌ DRIVE_FOLDER_ID not configured\n"
            "   How to get your folder ID:\n"
            "   1. Open your Google Drive folder with notebooks\n"
            "   2. Look at the URL: https://drive.google.com/drive/folders/YOUR_ID_HERE\n"
            "   3. Copy the YOUR_ID_HERE part\n"
            "   OR use 'root' for My Drive\n"
            "   Update line: DRIVE_FOLDER_ID = 'your_actual_folder_id_here'"
        )
    elif DRIVE_FOLDER_ID != "root" and len(DRIVE_FOLDER_ID) < 20:
        errors.append(
            "⚠ DRIVE_FOLDER_ID seems too short\n"
            "   Google Drive IDs are usually 25+ characters (or use 'root' for My Drive)"
        )
    
    # Check Owner
    if OWNER == "your_username":
        errors.append(
            "❌ OWNER not configured\n"
            "   Update line: OWNER = 'your_github_username'"
        )
    
    if errors:
        print("=" * 70)
        print("CONFIGURATION ERRORS FOUND")
        print("=" * 70)
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error}")
        print("\n" + "=" * 70)
        print("Please fix the errors above and try again.")
        print("=" * 70)
        return False
    
    print("✓ Configuration validated successfully!")
    print(f"  GitHub: {OWNER}/{REPO}")
    folder_display = "My Drive (root)" if DRIVE_FOLDER_ID == "root" else DRIVE_FOLDER_ID[:30] + "..."
    print(f"  Drive Folder: {folder_display}")
    print()
    return True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def mount_drive():
    """Mount Google Drive"""
    drive.mount('/content/drive')
    print("✓ Drive mounted successfully")

def get_folder_structure(drive_service, folder_id, path=""):
    """Recursively get all files and folders from Google Drive"""
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, webContentLink)',
        pageSize=1000
    ).execute()
    
    files_dict = {}
    for item in results.get('files', []):
        if item['mimeType'] == 'application/vnd.google.apps.folder':
            # Recursively get files from subfolder
            subfolder_files = get_folder_structure(
                drive_service, 
                item['id'], 
                path + item['name'] + '/'
            )
            files_dict.update(subfolder_files)
        elif item['name'].endswith('.ipynb'):
            files_dict[path + item['name']] = item
    
    return files_dict

def export_notebook_from_drive(drive_service, file_id):
    """
    Download notebook from Google Drive
    Handles both Google Colab files and regular .ipynb files
    """
    try:
        # First, try to export as Colab file
        try:
            request = drive_service.files().export_media(
                fileId=file_id,
                mimeType='application/ipynb'
            )
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            notebook_content = fh.getvalue()
            fh.close()
            
            # Verify it's valid JSON and has cells
            notebook_json = json.loads(notebook_content)
            if 'cells' in notebook_json:
                return notebook_content
        except:
            # If export fails, it's probably a regular .ipynb file, not Colab format
            pass
        
        # If export failed, download as regular file using alt='media'
        request = drive_service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        notebook_content = fh.getvalue()
        fh.close()
        
        # Verify it's valid JSON and has cells
        notebook_json = json.loads(notebook_content)
        if 'cells' not in notebook_json:
            print(f"  ⚠ Warning: Downloaded file missing 'cells' key")
            return None
        
        return notebook_content
        
    except Exception as e:
        print(f"  ❌ Error downloading notebook: {e}")
        return None

def upload_to_github(file_path, notebook_content, headers):
    """Upload notebook to GitHub"""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{file_path}"
    
    # Check if file already exists
    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json()["sha"]
    
    # Prepare payload
    payload = {
        "message": f"Sync: {file_path}",
        "content": base64.b64encode(notebook_content).decode('utf-8'),
        "branch": BRANCH
    }
    
    if sha:
        payload["sha"] = sha
    
    # Upload/Update file
    resp = requests.put(url, headers=headers, json=payload)
    
    return resp.status_code, resp.text

# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_notebooks():
    """Main function to sync all notebooks"""
    print("="*70)
    print("GOOGLE DRIVE TO GITHUB NOTEBOOK SYNC")
    print("="*70)
    print()
    
    # Validate configuration first
    if not validate_configuration():
        return
    
    # Authenticate with Google Drive
    print("\n1. Authenticating with Google Drive...")
    drive_service = build('drive', 'v3')
    print("✓ Authenticated")
    
    # Get folder structure
    print(f"\n2. Scanning Google Drive folder...")
    try:
        files_dict = get_folder_structure(drive_service, DRIVE_FOLDER_ID)
        print(f"✓ Found {len(files_dict)} notebook(s)")
    except Exception as e:
        print(f"\n❌ Error accessing Google Drive folder:")
        print(f"   {str(e)}")
        print(f"\n   Possible causes:")
        print(f"   1. DRIVE_FOLDER_ID is incorrect or has not been updated")
        print(f"   2. You don't have access to the folder")
        print(f"   3. The folder has been deleted")
        print(f"\n   Current DRIVE_FOLDER_ID: {DRIVE_FOLDER_ID}")
        return
    
    if len(files_dict) == 0:
        print("❌ No notebooks found. Check DRIVE_FOLDER_ID")
        return
    
    # Set up GitHub headers
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    # Sync statistics
    uploaded = 0
    updated = 0
    failed = 0
    skipped = 0
    
    # Download and upload each notebook
    print("\n3. Syncing notebooks to GitHub...")
    print("-" * 70)
    
    for file_path, file_info in sorted(files_dict.items()):
        print(f"\nProcessing: {file_path}")
        
        # Export notebook from Google Drive
        print(f"  Downloading from Drive...", end=" ")
        notebook_content = export_notebook_from_drive(drive_service, file_info['id'])
        
        if notebook_content is None:
            print("❌ Failed to export")
            failed += 1
            continue
        
        print("✓")
        
        # Validate content
        try:
            notebook_json = json.loads(notebook_content)
            if not notebook_json.get('cells'):
                print(f"  ⚠ Skipped (empty notebook)")
                skipped += 1
                continue
        except:
            print(f"  ⚠ Invalid JSON, skipping")
            failed += 1
            continue
        
        # Upload to GitHub
        print(f"  Uploading to GitHub...", end=" ")
        status_code, response_text = upload_to_github(file_path, notebook_content, headers)
        
        if status_code == 201:
            print("✓ Created")
            uploaded += 1
        elif status_code == 200:
            print("✓ Updated")
            updated += 1
        else:
            print(f"❌ Error ({status_code})")
            print(f"    Response: {response_text[:100]}")
            failed += 1
    
    # Print summary
    print("\n" + "="*70)
    print("SYNC COMPLETE - SUMMARY")
    print("="*70)
    print(f"✓ Uploaded:  {uploaded}")
    print(f"✓ Updated:   {updated}")
    print(f"⚠ Skipped:   {skipped}")
    print(f"❌ Failed:   {failed}")
    print(f"Total:       {uploaded + updated + skipped + failed}")
    print("="*70)
    
    if failed > 0:
        print(f"\n⚠ WARNING: {failed} notebook(s) failed to sync")
    else:
        print("\n✅ All notebooks synced successfully!")

# ============================================================================
# RUN THE SYNC
# ============================================================================

if __name__ == "__main__":
    try:
        sync_notebooks()
    except Exception as e:
        print(f"\n{'='*70}")
        print("❌ FATAL ERROR")
        print(f"{'='*70}")
        print(f"\nError: {e}")
        print(f"\nCommon fixes:")
        print(f"  1. Make sure GITHUB_TOKEN is set correctly")
        print(f"  2. Make sure DRIVE_FOLDER_ID is set correctly")
        print(f"  3. Check that both are actual values, not placeholder text")
        print(f"  4. Make sure you have access to the Google Drive folder")
        print(f"\nFull traceback:")
        import traceback
        traceback.print_exc()
        print(f"\n{'='*70}")
