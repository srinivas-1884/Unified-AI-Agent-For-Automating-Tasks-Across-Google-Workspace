from __future__ import print_function
import os
import pickle
import pathlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define all the scopes you need for the complete Workspace Agent
SCOPES = [
    # Drive scopes
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
    
    # Gmail scope
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    
    # Tasks scope
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/tasks.readonly",
    
    # Calendar scope (includes Meet creation)
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.owned",  # For creating events
]

def authenticate():
    """Authenticate and generate token.json with all required scopes."""
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"  # your OAuth client credentials file

    print("\n🔐 Workspace Agent Authentication")
    print("=" * 50)
    print("This will request access to:")
    print("  📁 Google Drive - Read files")
    print("  📧 Gmail - Send emails")
    print("  📋 Google Tasks - Manage tasks")
    print("  📅 Google Calendar - Manage events and create Google Meet")
    print("  📝 Google Keep - Notes (local storage)")
    print("=" * 50)

    # Check if credentials.json exists
    if not os.path.exists(creds_path):
        print(f"\n❌ Error: {creds_path} not found!")
        print("\nPlease download your OAuth client credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to 'APIs & Services' > 'Credentials'")
        print("4. Create OAuth 2.0 Client ID (Desktop application)")
        print("5. Download JSON and save as 'credentials.json'")
        return

    # Check if old token exists and show scopes
    if os.path.exists(token_path):
        try:
            old_creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print(f"\n📋 Current token scopes: {old_creds.scopes}")
            
            # Check if all required scopes are present
            missing_scopes = [s for s in SCOPES if s not in old_creds.scopes]
            if missing_scopes:
                print(f"\n⚠️  Missing scopes: {missing_scopes}")
                print("🔄 Will regenerate token with all required scopes.")
                os.remove(token_path)
                print("✅ Old token.json removed.")
            else:
                print("✅ Token already has all required scopes.")
                use_existing = input("\nUse existing token? (y/n): ").lower()
                if use_existing != 'y':
                    os.remove(token_path)
                    print("✅ Old token.json removed. Will generate new one.")
        except Exception as e:
            print(f"⚠️  Error reading existing token: {e}")
            if os.path.exists(token_path):
                os.remove(token_path)
                print("✅ Invalid token removed. Will generate new one.")
    else:
        print("\n🆕 No existing token found. Will generate new one.")

    # Run OAuth flow
    print("\n🔄 Opening browser for authentication...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)

        # Save new token
        with open(token_path, "w") as token:
            token.write(creds.to_json())

        print("\n" + "=" * 50)
        print("✅ Authentication successful!")
        print(f"📋 Granted scopes: {creds.scopes}")
        print(f"💾 Token saved to: {token_path}")
        print("=" * 50)
        
        # Verify all scopes were granted
        granted_scopes = creds.scopes
        missing_after = [s for s in SCOPES if s not in granted_scopes]
        if missing_after:
            print(f"\n⚠️  Warning: Some scopes were not granted: {missing_after}")
            print("You may need to:")
            print("1. Go to https://myaccount.google.com/permissions")
            print("2. Remove access for this app")
            print("3. Run authentication again")
        else:
            print("\n✅ All required scopes granted successfully!")

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure 'credentials.json' is valid")
        print("2. Check that all required APIs are enabled in Google Cloud Console:")
        print("   - Google Calendar API")
        print("   - Google Meet API")
        print("3. Go to https://console.cloud.google.com/apis/library")

if __name__ == "__main__":
    import sys
    
    print("\n🔐 Google Workspace Agent - Authentication Tool")
    print("=" * 50)
    
    authenticate()
    
   