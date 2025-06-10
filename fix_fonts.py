#!/usr/bin/env python3
"""
Simple Font Fixer

Removes improperly installed fonts and reinstalls them correctly.
"""

import os
import subprocess
import shutil
from pathlib import Path
import tempfile
import zipfile


def clear_user_fonts():
    """Clear the user fonts directory."""
    user_fonts = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    
    if user_fonts.exists():
        print(f"🧹 Clearing user fonts directory: {user_fonts}")
        try:
            shutil.rmtree(user_fonts)
            print("✅ User fonts directory cleared")
        except Exception as e:
            print(f"❌ Failed to clear user fonts: {e}")
    else:
        print("ℹ️  User fonts directory doesn't exist")


def install_fonts_powershell():
    """Use PowerShell to install fonts properly."""
    downloads_dir = Path("./downloads/fonts")
    
    if not downloads_dir.exists():
        print("❌ No downloads/fonts directory found!")
        return
    
    print("🎨 Installing fonts using PowerShell method")
    print("=" * 50)
    
    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        all_fonts_dir = temp_path / "all_fonts"
        all_fonts_dir.mkdir()
        
        # Extract all fonts to single directory
        zip_files = list(downloads_dir.rglob("*.zip"))
        print(f"📦 Extracting {len(zip_files)} font packages...")
        
        font_count = 0
        for zip_file in zip_files:
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.lower().endswith(('.ttf', '.otf')):
                            # Extract with clean filename
                            clean_name = Path(file_info.filename).name
                            extract_path = all_fonts_dir / clean_name
                            
                            with open(extract_path, 'wb') as f:
                                f.write(zip_ref.read(file_info))
                            font_count += 1
            except Exception as e:
                print(f"❌ Failed to extract {zip_file.name}: {e}")
        
        print(f"✅ Extracted {font_count} font files")
        
        # Create PowerShell script to install fonts
        ps_script = f'''
# PowerShell Font Installation Script
$ErrorActionPreference = "Continue"

Write-Host "🎨 Installing fonts using PowerShell..."

# Get all font files
$fontFiles = Get-ChildItem -Path "{all_fonts_dir}" -Include *.ttf,*.otf -Recurse

Write-Host "Found $($fontFiles.Count) font files"

$installed = 0
$failed = 0

foreach ($font in $fontFiles) {{
    try {{
        Write-Host "Installing: $($font.Name)" -ForegroundColor Yellow
        
        # Copy to user fonts directory
        $userFontsPath = "$env:LOCALAPPDATA\\Microsoft\\Windows\\Fonts"
        if (!(Test-Path $userFontsPath)) {{
            New-Item -ItemType Directory -Path $userFontsPath -Force | Out-Null
        }}
        
        $destPath = Join-Path $userFontsPath $font.Name
        Copy-Item $font.FullName $destPath -Force
        
        # Register font
        Add-Type -AssemblyName System.Drawing
        $fontFamily = New-Object System.Drawing.Text.PrivateFontCollection
        $fontFamily.AddFontFile($destPath)
        
        Write-Host "  ✅ $($font.Name)" -ForegroundColor Green
        $installed++
    }}
    catch {{
        Write-Host "  ❌ $($font.Name): $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }}
}}

Write-Host ""
Write-Host "=" * 50
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host "✅ Installed: $installed fonts" -ForegroundColor Green
Write-Host "❌ Failed: $failed fonts" -ForegroundColor Red

# Refresh font cache
Write-Host "🔄 Refreshing font cache..."
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class FontHelper {{
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    
    public static void RefreshFonts() {{
        SendMessage((IntPtr)0xFFFF, 0x001D, IntPtr.Zero, IntPtr.Zero);
    }}
}}
"@
[FontHelper]::RefreshFonts()

Write-Host "✅ Font cache refreshed"
Write-Host ""
Write-Host "💡 Fonts should now be available in applications!"
Write-Host "   If not visible immediately, restart the application."
'''
        
        # Save PowerShell script
        ps_script_path = temp_path / "install_fonts.ps1"
        with open(ps_script_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        print("\n🚀 Running PowerShell font installer...")
        
        # Run PowerShell script
        try:
            result = subprocess.run([
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass",
                "-File", str(ps_script_path)
            ], capture_output=True, text=True, cwd=str(temp_path))
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
                
        except Exception as e:
            print(f"❌ Failed to run PowerShell script: {e}")


def main():
    """Main function."""
    print("🔧 Font Installation Fixer")
    print("=" * 30)
    print()
    
    choice = input("Do you want to clear existing user fonts first? (y/n): ").lower().strip()
    
    if choice == 'y':
        clear_user_fonts()
        print()
    
    install_fonts_powershell()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
