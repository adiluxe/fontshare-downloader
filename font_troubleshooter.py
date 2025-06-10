#!/usr/bin/env python3
"""
Font Installation Troubleshooter

Diagnoses and fixes font installation issues on Windows.
"""

import os
import shutil
import zipfile
import tempfile
import ctypes
from pathlib import Path


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def clean_user_fonts():
    """Remove all fonts from user directory."""
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    print(f"🧹 Cleaning user fonts directory: {user_fonts}")
    
    if user_fonts.exists():
        try:
            # Remove all font files
            for font_file in user_fonts.glob("*"):
                if font_file.is_file() and font_file.suffix.lower() in ['.ttf', '.otf']:
                    font_file.unlink()
                    print(f"  🗑️  Removed: {font_file.name}")
            print("✅ User fonts directory cleaned")
        except Exception as e:
            print(f"❌ Failed to clean user fonts: {e}")
    else:
        print("ℹ️  User fonts directory doesn't exist")


def install_test_fonts_to_system():
    """Install a few test fonts directly to system directory."""
    
    if not is_admin():
        print("❌ This operation requires administrator privileges!")
        print("Please right-click and 'Run as administrator'")
        return False
    
    downloads_dir = Path("./downloads/fonts")
    system_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    
    print(f"🎯 Installing test fonts to: {system_fonts}")
    
    # Test with these popular fonts
    test_fonts = ["satoshi", "cabinet-grotesk", "clash-display"]
    installed_any = False
    
    for font_name in test_fonts:
        font_zip = downloads_dir / font_name / f"{font_name}.zip"
        
        if not font_zip.exists():
            print(f"⚠️  {font_name}.zip not found")
            continue
        
        print(f"📦 Installing: {font_name}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Extract ZIP
                with zipfile.ZipFile(font_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find font files - just take the regular variant
                font_files = []
                for pattern in ["*Regular.ttf", "*-Regular.ttf", "*.ttf"]:
                    found = list(temp_path.rglob(pattern))
                    if found:
                        font_files = found[:1]  # Just take first one
                        break
                
                if font_files:
                    for font_file in font_files:
                        dest = system_fonts / font_file.name
                        
                        try:
                            # Copy to system fonts
                            shutil.copy2(font_file, dest)
                            print(f"  ✅ Copied: {font_file.name}")
                            installed_any = True
                            
                            # Register font using Windows API
                            gdi32 = ctypes.windll.gdi32
                            user32 = ctypes.windll.user32
                            
                            result = gdi32.AddFontResourceW(str(dest))
                            if result > 0:
                                user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  # WM_FONTCHANGE
                                print(f"  🔄 Registered: {font_file.name}")
                            
                        except Exception as e:
                            print(f"  ❌ Failed: {font_file.name} - {e}")
                else:
                    print(f"  ⚠️  No font files found in {font_name}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {font_name}: {e}")
    
    return installed_any


def main():
    print("🔧 Font Installation Troubleshooter")
    print("=" * 40)
    print(f"👤 Running as Administrator: {'Yes' if is_admin() else 'No'}")
    print()
    
    # Step 1: Clean existing installations
    print("Step 1: Cleaning existing font installations...")
    clean_user_fonts()
    print()
    
    # Step 2: Install test fonts to system
    print("Step 2: Installing test fonts to system directory...")
    if install_test_fonts_to_system():
        print()
        print("=" * 50)
        print("🎉 Test Installation Complete!")
        print("=" * 50)
        print("📝 Installed popular fonts to C:\\Windows\\Fonts")
        print()
        print("🧪 TEST NOW:")
        print("1. Open Microsoft Word")
        print("2. Click the font dropdown")
        print("3. Look for these fonts:")
        print("   • Satoshi")
        print("   • Cabinet Grotesk") 
        print("   • Clash Display")
        print()
        print("If you see these fonts, the system method works!")
        print("Then we can install ALL fonts the same way.")
    else:
        print("❌ Test installation failed")
        print("This might be a Windows permissions or system issue.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
