#!/usr/bin/env python3
"""
Font Extractor for Manual Installation

Extracts all fonts to user fonts directory for easy manual installation.
"""

import os
import zipfile
import shutil
from pathlib import Path
import tempfile


def extract_all_fonts_for_manual_install():
    """Extract all fonts to user directory for manual installation."""
    
    downloads_dir = Path("./downloads/fonts")
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    # Create user fonts directory
    user_fonts.mkdir(parents=True, exist_ok=True)
    
    print("🎨 Font Extractor for Manual Installation")
    print("=" * 50)
    print(f"📁 Source: {downloads_dir}")
    print(f"📁 Target: {user_fonts}")
    print()
    
    # Clear existing fonts first
    print("🧹 Clearing existing fonts...")
    for existing_font in user_fonts.glob("*"):
        if existing_font.is_file() and existing_font.suffix.lower() in ['.ttf', '.otf']:
            try:
                existing_font.unlink()
                print(f"  🗑️  Removed: {existing_font.name}")
            except:
                pass
    
    print("✅ User fonts directory cleared")
    print()
    
    # Find all ZIP files
    zip_files = list(downloads_dir.rglob("*.zip"))
    
    if not zip_files:
        print("❌ No font ZIP files found!")
        return
    
    print(f"📦 Found {len(zip_files)} font packages")
    print("🔄 Extracting all fonts...")
    print()
    
    total_fonts = 0
    processed_packages = 0
    
    for zip_file in zip_files:
        font_name = zip_file.stem
        print(f"Extracting: {font_name}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(('.ttf', '.otf')):
                        # Extract with clean filename
                        clean_name = Path(file_info.filename).name
                        
                        # Read file content
                        font_content = zip_ref.read(file_info)
                        
                        # Write to user fonts directory
                        font_path = user_fonts / clean_name
                        with open(font_path, 'wb') as f:
                            f.write(font_content)
                        
                        print(f"  ✅ {clean_name}")
                        total_fonts += 1
            
            processed_packages += 1
            
        except Exception as e:
            print(f"  ❌ Failed to process {font_name}: {e}")
    
    print()
    print("=" * 60)
    print("🎉 Font Extraction Complete!")
    print("=" * 60)
    print(f"📦 Processed packages: {processed_packages}")
    print(f"📝 Total font files: {total_fonts}")
    print(f"📁 Location: {user_fonts}")
    print()
    print("🎯 MANUAL INSTALLATION STEPS:")
    print("=" * 30)
    print("1. Open File Explorer")
    print("2. Navigate to:")
    print(f"   {user_fonts}")
    print("3. Press Ctrl+A to select all fonts")
    print("4. Right-click and select 'Install' or 'Install for all users'")
    print("5. Wait for Windows to install all fonts")
    print()
    print("💡 Alternative method:")
    print("1. Select all fonts (Ctrl+A)")
    print("2. Copy them (Ctrl+C)")
    print("3. Open C:\\Windows\\Fonts in File Explorer")
    print("4. Paste the fonts (Ctrl+V)")
    print()
    print("✨ After installation, fonts will appear immediately in all apps!")


def open_fonts_directory():
    """Open the user fonts directory in File Explorer."""
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    if user_fonts.exists():
        print(f"🔍 Opening fonts directory: {user_fonts}")
        os.system(f'explorer "{user_fonts}"')
    else:
        print("❌ Fonts directory doesn't exist yet!")


def main():
    """Main function."""
    print("Choose an option:")
    print("1. Extract all fonts for manual installation")
    print("2. Open fonts directory in File Explorer")
    print("3. Both - extract and open directory")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            extract_all_fonts_for_manual_install()
        elif choice == "2":
            open_fonts_directory()
        elif choice == "3":
            extract_all_fonts_for_manual_install()
            print("\n🔍 Opening fonts directory...")
            open_fonts_directory()
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
