import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from rich import print
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

NUMLOOKUP_API_KEY = os.getenv("NUMLOOKUP_API_KEY")

console = Console()

def numlookup_api(phone):
    if not NUMLOOKUP_API_KEY:
        return {"error": "API key not found in .env file"}

    url = f"https://api.numlookupapi.com/v1/validate/{phone}?apikey={NUMLOOKUP_API_KEY}"
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"NumLookup API failed (status {r.status_code})"}
    except Exception as e:
        return {"error": str(e)}

def phone_basic_info(phone):
    try:
        parsed = phonenumbers.parse(phone, None)

        country = geocoder.description_for_number(parsed, "en")
        region_code = phonenumbers.region_code_for_number(parsed)

        # Try to extract state/region more clearly
        location = geocoder.description_for_number(parsed, "en")
        state = "Unknown"

        if "," in location:
            state = location.split(",")[0].strip()
        else:
            state = location

        info = {
            "valid": phonenumbers.is_valid_number(parsed),
            "possible": phonenumbers.is_possible_number(parsed),
            "country": country,
            "region_code": region_code,
            "state_or_region": state,
            "carrier": carrier.name_for_number(parsed, "en"),
            "timezone": ", ".join(timezone.time_zones_for_number(parsed)),
            "international_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "e164_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        }

        return info
    except Exception as e:
        return {"error": "Invalid phone number"}


def osint_links(phone):
    clean = phone.replace("+", "").replace(" ", "")

    

def display_results(basic, numlookup, links):
    table = Table(title="📱 Phone Number OSINT Report", show_lines=True)

    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Details", style="green")

    # Basic info
    table.add_row("Valid Number", str(basic.get("valid", "N/A")))
    table.add_row("Possible Number", str(basic.get("possible", "N/A")))
    table.add_row("Country", basic.get("country", "N/A"))
    table.add_row("State/Region", basic.get("state_or_region", "N/A"))
    table.add_row("Carrier", basic.get("carrier", "N/A"))
    table.add_row("Timezone", basic.get("timezone", "N/A"))
    table.add_row("International Format", basic.get("international_format", "N/A"))
    table.add_row("National Format", basic.get("national_format", "N/A"))
    table.add_row("E164 Format", basic.get("e164_format", "N/A"))

    # NumLookup info
    if "error" not in numlookup:
        table.add_row("Caller Name", str(numlookup.get("name", "N/A")))
        table.add_row("Line Type", str(numlookup.get("line_type", "N/A")))
        table.add_row("Location", str(numlookup.get("location", "N/A")))
        table.add_row("Carrier (API)", str(numlookup.get("carrier", "N/A")))
        table.add_row("Country Code", str(numlookup.get("country_code", "N/A")))
    else:
        table.add_row("NumLookup", numlookup["error"])

    console.print(table)

   
def main():
    print("\nADVANCED PHONE NUMBER OSINT TOOL \n")
    phone = input("Enter phone number (with country code, e.g. +14155552671): ").strip()

    basic = phone_basic_info(phone)
    numlookup = numlookup_api(phone)
    links = osint_links(phone)

    display_results(basic, numlookup, links)

if __name__ == "__main__":
    main()
