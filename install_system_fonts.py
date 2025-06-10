#!/usr/bin/env python3
"""
System Font Installer

Installs fonts to C:\Windows\Fonts (requires administrator privileges)
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path


def install_system_fonts():
    """Install fonts to system directory."""
    
    # Check if running as admin
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("❌ This script requires administrator privileges!")
            print("Please run the .bat file as administrator.")
            return
    except:
        print("⚠️  Could not verify admin privileges")
    
    downloads_dir = Path("./downloads/fonts")
    system_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    
    if not downloads_dir.exists():
        print("❌ No downloads/fonts directory found!")
        return
        
    if not system_fonts.exists():
        print("❌ System fonts directory not found!")
        return
    
    print("🎨 System Font Installer")
    print("=" * 30)
    print(f"📁 Source: {downloads_dir}")
    print(f"📁 Target: {system_fonts}")
    print()
    
    # Find all ZIP files
    zip_files = list(downloads_dir.rglob("*.zip"))
    
    if not zip_files:
        print("❌ No font ZIP files found!")
        return
    
    print(f"Found {len(zip_files)} font packages")
    print()
    
    installed_count = 0
    total_fonts = 0
    
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
                    package_success = True
                    # Copy font files to system fonts directory
                    for font_file in font_files:
                        total_fonts += 1
                        dest = system_fonts / font_file.name
                        try:
                            shutil.copy2(font_file, dest)
                            print(f"  ✅ {font_file.name}")
                        except Exception as e:
                            print(f"  ❌ {font_file.name}: {e}")
                            package_success = False
                    
                    if package_success:
                        installed_count += 1
                else:
                    print(f"  ⚠️  No font files found in {font_name}")
                    
            except Exception as e:
                print(f"  ❌ Failed to process {font_name}: {e}")
    
    print()
    print("=" * 50)
    print(f"🎉 System Installation Complete!")
    print(f"✅ Installed {installed_count} font packages")
    print(f"📝 Total font files: {total_fonts}")
    print(f"📁 Location: {system_fonts}")
    print()
    print("💡 System fonts are immediately available to all applications!")
    print("   No restart required - fonts should appear right away.")


if __name__ == "__main__":
    try:
        install_system_fonts()
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to exit...")
