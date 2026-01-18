
import os
import sys
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

def verify_exports():
    # Setup
    client = TestClient(app)
    
    # Create output directory
    output_dir = "verify_exports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Output directory: {os.path.abspath(output_dir)}")

    # Create valid token for the default admin user
    access_token = create_access_token(data={"sub": "admin@temple.com", "id": 1, "scopes": ["*"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    today = date.today().isoformat()
    
    endpoints = [
        {
            "name": "Donations Excel",
            "url": f"/api/v1/donations/export/excel?date_from={today}&date_to={today}",
            "ext": "xlsx",
            "expected_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        {
            "name": "Donations PDF",
            "url": f"/api/v1/donations/export/pdf?date_from={today}&date_to={today}",
            "ext": "pdf",
            "expected_type": "application/pdf"
        },
        {
            "name": "Seva Report Excel",
            "url": f"/api/v1/reports/sevas/detailed/export/excel?from_date={today}&to_date={today}",
            "ext": "xlsx",
            "expected_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        {
            "name": "Seva Report PDF",
            "url": f"/api/v1/reports/sevas/detailed/export/pdf?from_date={today}&to_date={today}",
            "ext": "pdf",
            "expected_type": "application/pdf"
        }
    ]
    
    success_count = 0
    
    print("\n--- Starting Verification ---")
    
    for ep in endpoints:
        print(f"\nVerifying {ep['name']}...")
        try:
            response = client.get(ep["url"], headers=headers)
            
            if response.status_code == 200:
                # Check headers
                content_type = response.headers.get("content-type")
                if content_type == ep["expected_type"]:
                    print(f"✅ Status 200 OK")
                    print(f"✅ Content-Type matches: {content_type}")
                    
                    # Save file
                    filename = f"{ep['name'].lower().replace(' ', '_')}.{ep['ext']}"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    file_size = os.path.getsize(filepath)
                    print(f"✅ File saved: {filename} ({file_size} bytes)")
                    
                    if file_size > 0:
                        success_count += 1
                    else:
                        print("❌ Error: File is empty")
                else:
                    print(f"❌ Content-Type Mismatch: Expected {ep['expected_type']}, got {content_type}")
            else:
                print(f"❌ Failed with Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

    print("\n--- Summary ---")
    print(f"Total: {len(endpoints)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(endpoints) - success_count}")

if __name__ == "__main__":
    # Ensure we are in backend dir
    if os.getcwd().endswith("backend"):
        pass
    else:
        # try to switch to backend if existing
        if os.path.exists("backend"):
            os.chdir("backend")
            sys.path.append(os.getcwd())
    
    verify_exports()
