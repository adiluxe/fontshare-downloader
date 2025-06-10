#!/usr/bin/env python3
"""
Fontshare Font Installer

A tool to automatically install all downloaded fonts from Fontshare.
Supports Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import zipfile
import tempfile
import platform
from pathlib import Path
from typing import List, Dict
import logging

class FontInstaller:
    """Install fonts from downloaded ZIP files."""
    
    def __init__(self, fonts_dir: str = "./downloads/fonts"):
        self.fonts_dir = Path(fonts_dir)
        self.os_type = platform.system().lower()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fontshare_install_"))
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Get system font directory
        self.system_font_dir = self._get_system_font_directory()
        
    def _get_system_font_directory(self) -> Path:
        """Get the system font directory based on OS."""
        if self.os_type == "windows":
            return Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        elif self.os_type == "darwin":  # macOS
            return Path.home() / "Library" / "Fonts"
        else:  # Linux
            user_fonts = Path.home() / ".local" / "share" / "fonts"
            user_fonts.mkdir(parents=True, exist_ok=True)
            return user_fonts
    
    def extract_fonts_from_zip(self, zip_path: Path) -> List[Path]:
        """Extract font files from a ZIP archive."""
        font_files = []
        font_extensions = {'.ttf', '.otf', '.woff', '.woff2', '.eot'}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if any(file_info.filename.lower().endswith(ext) for ext in font_extensions):
                        # Extract to temp directory
                        extracted_path = zip_ref.extract(file_info, self.temp_dir)
                        font_files.append(Path(extracted_path))
                        
        except Exception as e:
            self.logger.error(f"Failed to extract {zip_path}: {e}")
            
        return font_files
    
    def install_font_windows(self, font_path: Path) -> bool:
        """Install font on Windows using registry."""
        try:
            import winreg
            
            # Copy font to Windows Fonts directory
            dest_path = self.system_font_dir / font_path.name
            shutil.copy2(font_path, dest_path)
            
            # Register font in registry
            font_name = font_path.stem
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                0, winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                registry_key, 
                f"{font_name} (TrueType)", 
                0, 
                winreg.REG_SZ, 
                font_path.name
            )
            winreg.CloseKey(registry_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install {font_path.name} on Windows: {e}")
            return False
    
    def install_font_simple_copy(self, font_path: Path) -> bool:
        """Simple font installation by copying to font directory."""
        try:
            dest_path = self.system_font_dir / font_path.name
            shutil.copy2(font_path, dest_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy {font_path.name}: {e}")
            return False
    
    def install_font(self, font_path: Path) -> bool:
        """Install a single font file."""
        if self.os_type == "windows":
            # Try admin installation first, fallback to simple copy
            try:
                return self.install_font_windows(font_path)
            except:
                self.logger.warning(f"Registry installation failed for {font_path.name}, trying simple copy...")
                return self.install_font_simple_copy(font_path)
        else:
            return self.install_font_simple_copy(font_path)
    
    def find_font_zips(self) -> List[Path]:
        """Find all font ZIP files in the downloads directory."""
        zip_files = []
        if self.fonts_dir.exists():
            zip_files = list(self.fonts_dir.rglob("*.zip"))
        return zip_files
    
    def install_all_fonts(self) -> Dict[str, int]:
        """Install all fonts from ZIP files."""
        zip_files = self.find_font_zips()
        
        if not zip_files:
            self.logger.warning(f"No font ZIP files found in {self.fonts_dir}")
            return {"processed": 0, "installed": 0, "failed": 0}
        
        self.logger.info(f"Found {len(zip_files)} font ZIP files")
        self.logger.info(f"Installing fonts to: {self.system_font_dir}")
        
        stats = {"processed": 0, "installed": 0, "failed": 0}
        
        for zip_path in zip_files:
            self.logger.info(f"Processing: {zip_path.name}")
            stats["processed"] += 1
            
            # Extract fonts from ZIP
            font_files = self.extract_fonts_from_zip(zip_path)
            
            if not font_files:
                self.logger.warning(f"No font files found in {zip_path.name}")
                stats["failed"] += 1
                continue
            
            # Install each font file
            zip_success = True
            for font_file in font_files:
                if self.install_font(font_file):
                    self.logger.info(f"✅ Installed: {font_file.name}")
                else:
                    self.logger.error(f"❌ Failed: {font_file.name}")
                    zip_success = False
            
            if zip_success:
                stats["installed"] += 1
            else:
                stats["failed"] += 1
        
        return stats
    
    def create_batch_installer(self):
        """Create a Windows batch file for easy installation."""
        batch_content = '''@echo off
echo Installing Fontshare Fonts...
echo.
echo This will install all downloaded fonts to your system.
echo You may need administrator privileges.
echo.
pause

python install_fonts.py

echo.
echo Installation complete!
echo.
pause
'''
        
        batch_path = Path("install_fonts.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        self.logger.info(f"Created batch installer: {batch_path}")
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def run(self):
        """Main execution method."""
        print("🎨 Fontshare Font Installer")
        print("=" * 40)
        print(f"Operating System: {platform.system()}")
        print(f"Font Directory: {self.system_font_dir}")
        print(f"Source Directory: {self.fonts_dir}")
        print()
        
        # Check if running as admin on Windows
        if self.os_type == "windows":
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    print("⚠️  Note: Running without administrator privileges.")
                    print("   Some fonts may not install properly.")
                    print("   Consider running as administrator for best results.")
                    print()
            except:
                pass
        
        try:
            stats = self.install_all_fonts()
            
            print("\n" + "=" * 50)
            print("🎉 Font Installation Complete!")
            print("=" * 50)
            print(f"📦 ZIP files processed: {stats['processed']}")
            print(f"✅ Successfully installed: {stats['installed']}")
            print(f"❌ Failed installations: {stats['failed']}")
            print(f"📁 Fonts installed to: {self.system_font_dir}")
            
            if self.os_type == "windows":
                print("\n💡 Tip: You may need to restart applications to see new fonts.")
            
        except KeyboardInterrupt:
            print("\n⚠️  Installation interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.logger.exception("Unexpected error occurred")
        finally:
            self.cleanup()


def main():
    """Command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Fontshare fonts")
    parser.add_argument(
        "--fonts-dir", 
        default="./downloads/fonts",
        help="Directory containing font ZIP files"
    )
    parser.add_argument(
        "--create-batch", 
        action="store_true",
        help="Create a batch installer file (Windows)"
    )
    
    args = parser.parse_args()
    
    installer = FontInstaller(args.fonts_dir)
    
    if args.create_batch:
        installer.create_batch_installer()
        print("✅ Batch installer created: install_fonts.bat")
        return
    
    installer.run()


if __name__ == "__main__":
    main()
