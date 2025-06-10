#!/usr/bin/env python3
"""
Proper Windows Font Installer

Uses Windows API to properly register fonts so they appear in applications.
"""

import os
import zipfile
import shutil
import tempfile
import ctypes
from pathlib import Path
from ctypes import wintypes
import winreg


class WindowsFontInstaller:
    """Proper Windows font installer that registers fonts with the system."""
    
    def __init__(self):
        self.downloads_dir = Path("./downloads/fonts")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fontshare_install_"))
        
        # Windows font directories
        self.system_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        self.user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
        
        # Ensure user fonts directory exists
        self.user_fonts.mkdir(parents=True, exist_ok=True)
        
    def is_admin(self):
        """Check if running as administrator."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def install_font_user_method(self, font_path: Path) -> bool:
        """Install font for current user using registry method."""
        try:
            # Copy font to user fonts directory
            dest_path = self.user_fonts / font_path.name
            shutil.copy2(font_path, dest_path)
            
            # Get font name for registry
            font_name = font_path.stem
            
            # Register in user registry
            key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                # Use relative path for user fonts
                winreg.SetValueEx(key, f"{font_name} (TrueType)", 0, winreg.REG_SZ, str(dest_path))
            
            return True
            
        except Exception as e:
            print(f"  ❌ Registry install failed for {font_path.name}: {e}")
            return False
    
    def install_font_system_method(self, font_path: Path) -> bool:
        """Install font system-wide (requires admin)."""
        try:
            # Copy to system fonts directory
            dest_path = self.system_fonts / font_path.name
            shutil.copy2(font_path, dest_path)
            
            # Register in system registry
            font_name = font_path.stem
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, f"{font_name} (TrueType)", 0, winreg.REG_SZ, font_path.name)
            
            return True
            
        except Exception as e:
            print(f"  ❌ System install failed for {font_path.name}: {e}")
            return False
    
    def install_font_winapi_method(self, font_path: Path) -> bool:
        """Install font using Windows API (most reliable)."""
        try:
            # Load required Windows APIs
            gdi32 = ctypes.windll.gdi32
            user32 = ctypes.windll.user32
            
            # Copy font to appropriate directory
            if self.is_admin():
                dest_path = self.system_fonts / font_path.name
                install_flag = 0  # System install
            else:
                dest_path = self.user_fonts / font_path.name
                install_flag = 1  # User install
                
            shutil.copy2(font_path, dest_path)
            
            # Use AddFontResource API to register the font
            result = gdi32.AddFontResourceW(str(dest_path))
            
            if result > 0:
                # Notify all windows that fonts have changed
                user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  # WM_FONTCHANGE to all windows
                return True
            else:
                print(f"  ❌ AddFontResource failed for {font_path.name}")
                return False
                
        except Exception as e:
            print(f"  ❌ WinAPI install failed for {font_path.name}: {e}")
            return False
    
    def extract_fonts_from_zip(self, zip_path: Path):
        """Extract font files from ZIP."""
        font_files = []
        font_extensions = {'.ttf', '.otf'}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if any(file_info.filename.lower().endswith(ext) for ext in font_extensions):
                        extracted_path = zip_ref.extract(file_info, self.temp_dir)
                        font_files.append(Path(extracted_path))
        except Exception as e:
            print(f"  ❌ Failed to extract {zip_path}: {e}")
            
        return font_files
    
    def install_font(self, font_path: Path) -> bool:
        """Install a font using the best available method."""
        # Try Windows API method first (most reliable)
        if self.install_font_winapi_method(font_path):
            return True
            
        # Fallback to registry method
        if self.install_font_user_method(font_path):
            return True
            
        # Last resort: try system method if admin
        if self.is_admin() and self.install_font_system_method(font_path):
            return True
            
        return False
    
    def refresh_font_cache(self):
        """Force Windows to refresh the font cache."""
        try:
            # Broadcast font change message
            user32 = ctypes.windll.user32
            user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  # WM_FONTCHANGE
            print("🔄 Font cache refreshed")
        except:
            print("⚠️  Could not refresh font cache")
    
    def run(self):
        """Main installation process."""
        print("🎨 Proper Windows Font Installer")
        print("=" * 40)
        print(f"👤 Administrator: {'Yes' if self.is_admin() else 'No'}")
        print(f"📁 System Fonts: {self.system_fonts}")
        print(f"📁 User Fonts: {self.user_fonts}")
        print()
        
        if not self.downloads_dir.exists():
            print("❌ No downloads/fonts directory found!")
            return
        
        # Find all font ZIP files
        zip_files = list(self.downloads_dir.rglob("*.zip"))
        
        if not zip_files:
            print("❌ No font ZIP files found!")
            return
        
        print(f"Found {len(zip_files)} font packages")
        print()
        
        success_count = 0
        total_fonts = 0
        
        for zip_file in zip_files:
            font_name = zip_file.stem
            print(f"Installing: {font_name}")
            
            # Extract fonts from ZIP
            font_files = self.extract_fonts_from_zip(zip_file)
            
            if not font_files:
                print(f"  ⚠️  No font files found in {font_name}")
                continue
            
            package_success = True
            for font_file in font_files:
                total_fonts += 1
                if self.install_font(font_file):
                    print(f"  ✅ {font_file.name}")
                else:
                    print(f"  ❌ {font_file.name}")
                    package_success = False
            
            if package_success:
                success_count += 1
        
        # Refresh font cache
        print()
        self.refresh_font_cache()
        
        print()
        print("=" * 50)
        print("🎉 Font Installation Complete!")
        print("=" * 50)
        print(f"✅ Successfully installed: {success_count} font packages")
        print(f"📝 Total font files: {total_fonts}")
        print(f"📁 Install location: {'System' if self.is_admin() else 'User'} fonts")
        print()
        print("💡 Next Steps:")
        print("  • Fonts should now appear in applications immediately")
        print("  • If not visible, restart the application")
        print("  • For stubborn apps, try logging out and back in")
        
        # Cleanup
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Run the font installer."""
    try:
        installer = WindowsFontInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
