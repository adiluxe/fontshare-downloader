#!/usr/bin/env python3
"""
Direct Font Extractor

Extracts all fonts to user directory and opens the folder automatically.
"""

import os
import zipfile
import subprocess
from pathlib import Path


def main():
    downloads_dir = Path("./downloads/fonts")
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    print("🎨 Extracting All Fonts for Manual Installation")
    print("=" * 55)
    print(f"📁 Source: {downloads_dir}")
    print(f"📁 Target: {user_fonts}")
    print()
    
    # Create user fonts directory
    user_fonts.mkdir(parents=True, exist_ok=True)
    
    # Clear existing fonts
    print("🧹 Clearing existing fonts...")
    cleared_count = 0
    for existing_font in user_fonts.glob("*"):
        if existing_font.is_file() and existing_font.suffix.lower() in ['.ttf', '.otf']:
            try:
                existing_font.unlink()
                cleared_count += 1
            except:
                pass
    
    print(f"✅ Cleared {cleared_count} existing fonts")
    print()
    
    # Find and extract all ZIP files
    zip_files = list(downloads_dir.rglob("*.zip"))
    print(f"📦 Found {len(zip_files)} font packages")
    print("🔄 Extracting...")
    print()
    
    total_fonts = 0
    
    for i, zip_file in enumerate(zip_files, 1):
        font_name = zip_file.stem
        print(f"[{i:2d}/{len(zip_files)}] {font_name}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                extracted_count = 0
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(('.ttf', '.otf')):
                        # Extract with clean filename
                        clean_name = Path(file_info.filename).name
                        font_content = zip_ref.read(file_info)
                        font_path = user_fonts / clean_name
                        
                        with open(font_path, 'wb') as f:
                            f.write(font_content)
                        
                        extracted_count += 1
                        total_fonts += 1
                
                print(f"         ✅ {extracted_count} fonts")
                
        except Exception as e:
            print(f"         ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("🎉 EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"📝 Total fonts extracted: {total_fonts}")
    print(f"📁 Location: {user_fonts}")
    print()
    print("🎯 MANUAL INSTALLATION STEPS:")
    print("-" * 30)
    print("1. The fonts folder will open automatically")
    print("2. Press Ctrl+A to select ALL fonts")
    print("3. Right-click and choose 'Install' or 'Install for all users'")
    print("4. Wait for Windows to install (may take a few minutes)")
    print("5. Fonts will appear in Word, Figma, etc. immediately!")
    print()
    print("💡 TIP: If 'Install for all users' option appears, use that")
    print("    for system-wide installation (requires admin approval)")
    print()
    
    # Open the fonts directory
    print("🔍 Opening fonts directory...")
    try:
        subprocess.run(['explorer', str(user_fonts)], check=True)
        print("✅ Fonts directory opened!")
    except Exception as e:
        print(f"❌ Could not open directory: {e}")
        print(f"📁 Please manually navigate to: {user_fonts}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
