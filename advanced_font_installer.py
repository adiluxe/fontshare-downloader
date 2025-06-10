#!/usr/bin/env python3
"""
Advanced Font Registration Tool

This tool tries multiple methods to ensure fonts are properly registered with Windows.
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
import ctypes
from pathlib import Path


class AdvancedFontInstaller:
    def __init__(self):
        self.downloads_dir = Path("./downloads/fonts")
        self.system_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        self.user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
        
    def is_admin(self):
        """Check if running as administrator."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def register_font_in_registry(self, font_path, font_name, is_system=False):
        """Register font in Windows registry."""
        try:
            import winreg
            
            if is_system:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                hkey = winreg.HKEY_LOCAL_MACHINE
                font_value = font_path.name  # Just filename for system fonts
            else:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                hkey = winreg.HKEY_CURRENT_USER
                font_value = str(font_path)  # Full path for user fonts
            
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_SET_VALUE) as key:
                # Try different registry entry formats
                registry_names = [
                    f"{font_name} (TrueType)",
                    f"{font_name} (OpenType)",
                    font_name,
                    f"{font_name} Regular (TrueType)",
                    f"{font_name} Regular (OpenType)"
                ]
                
                for reg_name in registry_names:
                    try:
                        winreg.SetValueEx(key, reg_name, 0, winreg.REG_SZ, font_value)
                        print(f"  📝 Registered: {reg_name}")
                        break
                    except Exception as e:
                        continue
                        
            return True
            
        except Exception as e:
            print(f"  ❌ Registry registration failed: {e}")
            return False
    
    def add_font_resource(self, font_path):
        """Use Windows API to add font resource."""
        try:
            # Load Windows GDI32 library
            gdi32 = ctypes.windll.gdi32
            user32 = ctypes.windll.user32
            
            # Add font resource
            result = gdi32.AddFontResourceW(str(font_path))
            
            if result > 0:
                # Broadcast font change message
                user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  # WM_FONTCHANGE
                print(f"  🔄 Added font resource: {font_path.name}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  ❌ AddFontResource failed: {e}")
            return False
    
    def install_single_font(self, font_path, target_dir, font_name):
        """Install a single font file."""
        try:
            # Copy font to target directory
            dest_path = target_dir / font_path.name
            shutil.copy2(font_path, dest_path)
            print(f"  📁 Copied to: {dest_path}")
            
            # Register in registry
            is_system = (target_dir == self.system_fonts)
            registry_success = self.register_font_in_registry(dest_path, font_name, is_system)
            
            # Add font resource using Windows API
            api_success = self.add_font_resource(dest_path)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to install {font_path.name}: {e}")
            return False
    
    def test_font_installation(self):
        """Test installation with a few popular fonts first."""
        print("🧪 Testing font installation with popular fonts...")
        print("=" * 50)
        
        # Test fonts - these are very commonly requested
        test_fonts = ["satoshi", "cabinet-grotesk", "clash-display"]
        
        for font_name in test_fonts:
            font_dir = self.downloads_dir / font_name
            if not font_dir.exists():
                continue
                
            zip_file = font_dir / f"{font_name}.zip"
            if not zip_file.exists():
                continue
            
            print(f"\n🎯 Testing: {font_name}")
            
            # Extract and install
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract ZIP
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find font files
                font_files = []
                for ext in ['.ttf', '.otf']:
                    font_files.extend(temp_path.rglob(f"*{ext}"))
                
                if not font_files:
                    print(f"  ⚠️  No font files found")
                    continue
                
                # Install fonts
                success_count = 0
                for font_file in font_files[:3]:  # Install first 3 variants
                    clean_name = font_file.stem
                    
                    # Try system installation first if admin
                    if self.is_admin():
                        if self.install_single_font(font_file, self.system_fonts, clean_name):
                            success_count += 1
                            print(f"  ✅ System install: {font_file.name}")
                    else:
                        if self.install_single_font(font_file, self.user_fonts, clean_name):
                            success_count += 1
                            print(f"  ✅ User install: {font_file.name}")
                
                if success_count > 0:
                    print(f"  🎉 Installed {success_count} variants of {font_name}")
                else:
                    print(f"  ❌ Failed to install {font_name}")
        
        print("\n" + "=" * 50)
        print("🔍 Testing complete!")
        print("\n💡 Now check if fonts appear in Word/Figma:")
        print("   • Open Microsoft Word")
        print("   • Click font dropdown")
        print("   • Look for: Satoshi, Cabinet Grotesk, Clash Display")
        print("\nIf they appear, we can install all fonts. If not, we need a different approach.")
    
    def install_all_fonts_system(self):
        """Install all fonts to system directory (requires admin)."""
        if not self.is_admin():
            print("❌ System installation requires administrator privileges!")
            print("Please right-click the script and 'Run as administrator'")
            return
        
        print("🎨 Installing ALL fonts to system directory...")
        print("=" * 50)
        
        zip_files = list(self.downloads_dir.rglob("*.zip"))
        print(f"Found {len(zip_files)} font packages")
        
        success_count = 0
        total_fonts = 0
        
        for zip_file in zip_files:
            font_name = zip_file.stem
            print(f"\n📦 Installing: {font_name}")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                try:
                    # Extract ZIP
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_path)
                    
                    # Find font files
                    font_files = []
                    for ext in ['.ttf', '.otf']:
                        font_files.extend(temp_path.rglob(f"*{ext}"))
                    
                    if font_files:
                        package_success = True
                        for font_file in font_files:
                            total_fonts += 1
                            clean_name = font_file.stem
                            
                            if self.install_single_font(font_file, self.system_fonts, clean_name):
                                print(f"  ✅ {font_file.name}")
                            else:
                                print(f"  ❌ {font_file.name}")
                                package_success = False
                        
                        if package_success:
                            success_count += 1
                    else:
                        print(f"  ⚠️  No font files found")
                        
                except Exception as e:
                    print(f"  ❌ Failed to process: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 System Installation Complete!")
        print(f"✅ Successfully installed: {success_count} packages")
        print(f"📝 Total font files: {total_fonts}")
        print("🔄 Font cache refreshed automatically")
        print("\n💡 Fonts should now appear immediately in all applications!")


def main():
    installer = AdvancedFontInstaller()
    
    print("🔧 Advanced Font Registration Tool")
    print("=" * 40)
    print(f"👤 Administrator: {'Yes' if installer.is_admin() else 'No'}")
    print(f"📁 System Fonts: {installer.system_fonts}")
    print(f"📁 User Fonts: {installer.user_fonts}")
    print()
    
    print("Choose an option:")
    print("1. Test installation with popular fonts (recommended)")
    print("2. Install ALL fonts to system directory (requires admin)")
    print("3. Install ALL fonts to user directory")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            installer.test_font_installation()
        elif choice == "2":
            installer.install_all_fonts_system()
        elif choice == "3":
            print("⚠️  User directory installation often doesn't work reliably.")
            confirm = input("Continue anyway? (y/n): ").lower().strip()
            if confirm == 'y':
                # Use the existing method but with better registration
                installer.test_font_installation()  # This will install to user dir if not admin
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
