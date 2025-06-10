#!/usr/bin/env python3
"""
Quick Font Installer for Windows

A simplified version that focuses on the most reliable installation method.
"""

import os
import zipfile
import shutil
from pathlib import Path
import tempfile


def install_fonts_simple():
    """Simple font installation by extracting and copying to User Fonts folder."""
    
    # Get paths - Use user fonts directory to avoid permission issues
    downloads_dir = Path("./downloads/fonts")
    
    # Try user fonts directory first (no admin required)
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    # Create user fonts directory if it doesn't exist
    try:
        user_fonts.mkdir(parents=True, exist_ok=True)
        fonts_dir = user_fonts
        install_type = "User"
    except:
        # Fallback to system fonts (requires admin)
        fonts_dir = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        install_type = "System"
    
    if not downloads_dir.exists():
        print("❌ No downloads/fonts directory found!")
        return
    
    print("🎨 Quick Font Installer (No Admin Required)")
    print("=" * 45)
    print(f"📁 Source: {downloads_dir}")
    print(f"📁 Target: {fonts_dir}")
    print(f"🔧 Install Type: {install_type} fonts")
    print()
    
    if install_type == "User":
        print("✅ Installing to user fonts directory (no admin required)")
        print("   Fonts will be available for your user account only")
    else:
        print("⚠️  Installing to system directory (admin required)")
    print()
    
    # Find all ZIP files
    zip_files = list(downloads_dir.rglob("*.zip"))
    
    if not zip_files:
        print("❌ No font ZIP files found!")
        return
    
    print(f"Found {len(zip_files)} font packages")
    print()
    
    installed_count = 0
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for zip_file in zip_files:
            font_name = zip_file.stem
            print(f"Installing: {font_name}")
            
            try:
                # Extract ZIP
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path / font_name)
                
                # Find font files
                font_extensions = ['.ttf', '.otf']
                font_files = []
                
                for ext in font_extensions:
                    font_files.extend((temp_path / font_name).rglob(f"*{ext}"))
                
                if font_files:
                    # Copy font files to Windows Fonts directory
                    for font_file in font_files:
                        dest = fonts_dir / font_file.name
                        try:
                            shutil.copy2(font_file, dest)
                            print(f"  ✅ {font_file.name}")
                        except Exception as e:
                            print(f"  ❌ {font_file.name}: {e}")
                    
                    installed_count += 1
                else:
                    print(f"  ⚠️  No font files found in {font_name}")
                    
            except Exception as e:
                print(f"  ❌ Failed to process {font_name}: {e}")
    
    print()
    print("=" * 50)
    print(f"🎉 Installation Complete!")
    print(f"✅ Installed {installed_count} font packages")
    print()
    print("💡 Tips:")
    print("  • Restart applications to see new fonts")
    print("  • If fonts don't appear, try logging out and back in")
    print("  • Some apps may need to be restarted")


if __name__ == "__main__":
    try:
        install_fonts_simple()
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to exit...")
