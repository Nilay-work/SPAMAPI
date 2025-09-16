import requests
import json
import os

API_URL = "https://momin-jwt.vercel.app/token?uid={}&password={}"

def generate_tokens(input_file):
    try:
        with open(input_file, "r") as f:
            accounts = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: '{input_file}' is not valid JSON or is empty.")
        return

    # Region-wise tokens collect karenge
    result = {}

    for account in accounts:
        uid = account.get("uid")
        password = account.get("password")

        if not uid or not password:
            print(f"⚠️ Skipping invalid account: {account}")
            continue

        try:
            print(f"Processing: {uid}", end=" ")

            response = requests.get(API_URL.format(uid, password), timeout=8)
            data = response.json()

            if "token" in data:
                # Region name extract karo
                region_code = (
                    data.get("lock_region") or 
                    data.get("notiRegion") or 
                    "UNKNOWN"
                ).upper()

                # Agar region nahi mila to UNKNOWN set
                if not region_code:
                    region_code = "UNKNOWN"

                # Result dict me add karo
                if region_code not in result:
                    result[region_code] = []

                result[region_code].append({
                    "uid": uid,
                    "token": data["token"]
                })

                print(f"✅ OK({region_code})")
            else:
                print("❌ FAIL(no token)")

        except Exception as e:
            print(f"❌ FAIL(error: {str(e)})")

    # Save region-wise JSON
    for region, tokens in result.items():
        if not tokens:
            continue

        # Region folder banao agar na ho
        folder = os.path.join(os.getcwd(), region)
        os.makedirs(folder, exist_ok=True)

        # File path
        filename = os.path.join(folder, f"token_{region.lower()}.json")

        with open(filename, "w") as f:
            json.dump(tokens, f, indent=4, separators=(",", ": "))

        print(f"💾 Saved {len(tokens)} tokens to {filename}")


# Run the function
if __name__ == "__main__":
    generate_tokens("accounts.json")
