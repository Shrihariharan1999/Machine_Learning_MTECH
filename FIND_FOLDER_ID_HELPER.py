# 🔍 HELPER SCRIPT: Find Folder ID in Google Drive
# Run this in Google Colab to find your "Colab Notebooks" folder ID

# Copy and paste this into a Colab cell and run it

from googleapiclient.discovery import build

print("Finding your Google Drive folders...")
print("="*70)

# Authenticate with Google Drive
drive_service = build('drive', 'v3')

# Search for all folders in My Drive
query = "mimeType='application/vnd.google.apps.folder' and trashed=false"
results = drive_service.files().list(
    q=query,
    spaces='drive',
    fields='files(id, name)',
    pageSize=50
).execute()

folders = results.get('files', [])

if not folders:
    print("No folders found in your Google Drive")
else:
    print(f"Found {len(folders)} folder(s) in your Google Drive:\n")
    
    for folder in folders:
        print(f"Folder Name: {folder['name']}")
        print(f"Folder ID:   {folder['id']}")
        print("-" * 70)
    
    print("\nLooking for 'Colab Notebooks'...\n")
    
    colab_folder = None
    for folder in folders:
        if "colab" in folder['name'].lower():
            print(f"✓ Found: {folder['name']}")
            print(f"  ID: {folder['id']}")
            print(f"\n  Use this ID in the sync script:")
            print(f"  DRIVE_FOLDER_ID = \"{folder['id']}\"")
            colab_folder = folder
            break
    
    if not colab_folder:
        print("⚠ Didn't find a 'Colab Notebooks' folder")
        print("  Your folder might have a different name")
        print("  Check the list above and use the ID for your notebooks folder")

print("\n" + "="*70)
