#!/usr/bin/env python3
"""
Test script to verify Fontshare download functionality
"""

import requests
import sys
from pathlib import Path


def test_font_download(font_name: str) -> bool:
    """Test downloading a single font to verify the API works."""
    
    url = f"https://api.fontshare.com/v2/fonts/download/{font_name}"
    
    print(f"Testing download for font: {font_name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
        
        if response.status_code == 200:
            # Check if it's actually a ZIP file
            content_type = response.headers.get('content-type', '').lower()
            if 'zip' in content_type or 'application/octet-stream' in content_type:
                print("✅ Successfully downloaded font ZIP file")
                
                # Save test file
                test_file = Path(f"test_{font_name}.zip")
                with open(test_file, 'wb') as f:
                    f.write(response.content)
                print(f"💾 Saved test file: {test_file}")
                
                return True
            else:
                print(f"❌ Unexpected content type: {content_type}")
                return False
        else:
            print(f"❌ Download failed with status {response.status_code}")
            if response.text:
                print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Test the download functionality with known fonts."""
    
    print("🧪 Fontshare Download Test")
    print("=" * 30)
    
    # Test fonts (some popular ones that should exist)
    test_fonts = ["satoshi", "cabinet-grotesk", "clash-display"]
    
    if len(sys.argv) > 1:
        # Use font name from command line
        test_fonts = [sys.argv[1]]
    
    success_count = 0
    
    for font_name in test_fonts:
        print(f"\nTesting: {font_name}")
        print("-" * 20)
        
        if test_font_download(font_name):
            success_count += 1
        
        print()
    
    print(f"📊 Test Results: {success_count}/{len(test_fonts)} successful")
    
    if success_count == len(test_fonts):
        print("🎉 All tests passed! The download API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the URLs or font names.")


if __name__ == "__main__":
    main()
