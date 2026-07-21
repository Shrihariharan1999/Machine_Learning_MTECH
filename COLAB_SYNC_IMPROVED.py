# ============================================================================
# IMPROVED GOOGLE DRIVE TO GITHUB SYNC SCRIPT FOR JUPYTER NOTEBOOKS
# ============================================================================
# This script properly downloads notebooks from Google Drive with all content
# and uploads them to GitHub while preserving folder structure.
# 
# Usage: Run this in Google Colab
# ============================================================================

import requests
import base64
from google.colab import drive
import os
import json
from io import BytesIO

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# GitHub Configuration
GITHUB_TOKEN = "your_github_token_here"  # Get from: https://github.com/settings/tokens
OWNER = "Shrihariharan1999"
REPO = "Machine_Learning_MTECH"
BRANCH = "main"

# Google Drive Configuration
DRIVE_FOLDER_ID = "your_google_drive_folder_id"  # The folder ID containing your notebooks

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
    Export notebook from Google Drive in .ipynb format
    This is the KEY fix - using export instead of get with alt='media'
    """
    try:
        # Use files().export_media for proper notebook export
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
        if 'cells' not in notebook_json:
            print(f"  ⚠ Warning: Exported notebook missing 'cells' key")
            return None
        
        return notebook_content
        
    except Exception as e:
        print(f"  ❌ Error exporting notebook: {e}")
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
    
    # Import required libraries
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    
    # Authenticate with Google Drive
    print("\n1. Authenticating with Google Drive...")
    drive_service = build('drive', 'v3')
    print("✓ Authenticated")
    
    # Get folder structure
    print(f"\n2. Scanning Google Drive folder (ID: {DRIVE_FOLDER_ID[:20]}...)...")
    files_dict = get_folder_structure(drive_service, DRIVE_FOLDER_ID)
    print(f"✓ Found {len(files_dict)} notebook(s)")
    
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
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
