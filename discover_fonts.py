"""
Enhanced font discovery script for Fontshare
This script attempts to discover fonts using multiple methods.
"""

import requests
import json
import re
from typing import List, Set


def discover_fonts_comprehensive() -> List[str]:
    """Comprehensive font discovery using multiple strategies."""
    
    all_fonts: Set[str] = set()
    
    print("🔍 Starting comprehensive font discovery...")
    
    # Strategy 1: Known popular fonts (always reliable)
    known_fonts = [
        "satoshi", "cabinet-grotesk", "clash-display", "general-sans",
        "switzer", "clash-grotesk", "supreme", "author", "zodiak",
        "eiko", "fraktion", "sohne", "poppins", "jakarta", 
        "inter", "space-grotesk", "nunito", "lexend", "chillax",
        "sentient", "tanker", "synonym", "boska", "author",
        "melodrama", "alpino", "ranade", "sohne-mono", "khand"
    ]
    
    print(f"✅ Added {len(known_fonts)} known fonts")
    all_fonts.update(known_fonts)
    
    # Strategy 2: Try to find API endpoints
    api_endpoints = [
        "https://api.fontshare.com/v2/fonts",
        "https://www.fontshare.com/api/fonts",
        "https://api.fontshare.com/fonts"
    ]
    
    for endpoint in api_endpoints:
        try:
            print(f"🌐 Trying API endpoint: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    extracted = extract_font_names_from_data(data)
                    if extracted:
                        print(f"✅ Found {len(extracted)} fonts from API")
                        all_fonts.update(extracted)
                        break
                except:
                    pass
        except Exception as e:
            print(f"❌ API endpoint failed: {e}")
    
    # Strategy 3: Brute force test common font naming patterns
    print("🔧 Testing common font patterns...")
    test_patterns = [
        # Single words
        "inter", "poppins", "roboto", "lato", "montserrat", "oswald", "raleway",
        "nunito", "ubuntu", "playfair", "merriweather", "lora", "crimson",
        # Hyphenated
        "open-sans", "source-sans", "pt-sans", "noto-sans", "work-sans",
        "ibm-plex", "red-hat", "fira-sans", "dm-sans", "plus-jakarta",
        # Grotesk family
        "aktiv-grotesk", "neue-grotesk", "atlas-grotesk", "founders-grotesk"
    ]
    
    valid_fonts = []
    for font in test_patterns:
        if test_font_exists(font):
            valid_fonts.append(font)
            all_fonts.add(font)
    
    if valid_fonts:
        print(f"✅ Found {len(valid_fonts)} additional fonts: {', '.join(valid_fonts[:5])}{'...' if len(valid_fonts) > 5 else ''}")
    
    result = sorted(list(all_fonts))
    print(f"\n📊 Total fonts discovered: {len(result)}")
    return result


def extract_font_names_from_data(data) -> List[str]:
    """Extract font names from API JSON data."""
    fonts = []
    
    if isinstance(data, dict):
        # Try common JSON structures
        for key in ['fonts', 'data', 'items', 'results']:
            if key in data:
                font_list = data[key]
                if isinstance(font_list, list):
                    for item in font_list:
                        if isinstance(item, dict):
                            name = item.get('slug') or item.get('name') or item.get('id')
                            if name:
                                fonts.append(name.lower().replace(' ', '-'))
                        elif isinstance(item, str):
                            fonts.append(item.lower().replace(' ', '-'))
    
    return fonts


def test_font_exists(font_name: str) -> bool:
    """Test if a font exists by trying to download it."""
    try:
        url = f"https://api.fontshare.com/v2/fonts/download/{font_name}"
        response = requests.head(url, timeout=5)  # Use HEAD to avoid downloading
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    fonts = discover_fonts_comprehensive()
    
    # Save to file
    with open("discovered_fonts.json", "w") as f:
        json.dump({
            "fonts": fonts,
            "count": len(fonts),
            "discovery_date": "2025-06-10"
        }, f, indent=2)
    
    print(f"\n💾 Saved font list to: discovered_fonts.json")
    print("\n📋 First 10 fonts:")
    for i, font in enumerate(fonts[:10]):
        print(f"  {i+1}. {font}")
    
    if len(fonts) > 10:
        print(f"  ... and {len(fonts) - 10} more")
