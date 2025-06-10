import os
import zipfile
from pathlib import Path

print("🎨 Fontshare Font Extractor for Manual Installation")
print("=" * 55)

# Set up paths
downloads_dir = Path("downloads/fonts")
user_fonts = Path("C:/Users/exequel/AppData/Local/Microsoft/Windows/Fonts")

# Create user fonts directory
user_fonts.mkdir(parents=True, exist_ok=True)
print(f"📁 Target directory: {user_fonts}")

# Clear existing fonts
print("🧹 Clearing existing fonts...")
cleared = 0
for font_file in user_fonts.glob("*"):
    if font_file.suffix.lower() in ['.ttf', '.otf']:
        font_file.unlink()
        cleared += 1

print(f"✅ Cleared {cleared} existing fonts")
print()

# Find all ZIP files
zip_files = []
for folder in downloads_dir.iterdir():
    if folder.is_dir():
        zip_path = folder / f"{folder.name}.zip"
        if zip_path.exists():
            zip_files.append(zip_path)

print(f"📦 Found {len(zip_files)} font packages")
print("🔄 Extracting all fonts...")
print()

total_fonts = 0
successful_packages = 0

for i, zip_file in enumerate(zip_files, 1):
    font_name = zip_file.stem
    print(f"[{i:2d}/{len(zip_files)}] {font_name}")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            font_count = 0
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(('.ttf', '.otf')):
                    # Get clean filename
                    clean_name = Path(file_info.filename).name
                    
                    # Read font data and write to user fonts directory
                    font_data = zip_ref.read(file_info)
                    font_path = user_fonts / clean_name
                    
                    with open(font_path, 'wb') as f:
                        f.write(font_data)
                    
                    font_count += 1
                    total_fonts += 1
            
            if font_count > 0:
                print(f"         ✅ {font_count} fonts")
                successful_packages += 1
            else:
                print(f"         ⚠️  No fonts found")
                
    except Exception as e:
        print(f"         ❌ Error: {e}")

print()
print("=" * 65)
print("🎉 FONT EXTRACTION COMPLETE!")
print("=" * 65)
print(f"📦 Successful packages: {successful_packages}/{len(zip_files)}")
print(f"📝 Total fonts extracted: {total_fonts}")
print(f"📁 Location: {user_fonts}")
print()
print("🎯 MANUAL INSTALLATION STEPS:")
print("-" * 35)
print("1. Open File Explorer (Windows + E)")
print("2. Navigate to:")
print(f"   {user_fonts}")
print("3. Press Ctrl+A to select ALL fonts")
print("4. Right-click and choose 'Install' or 'Install for all users'")
print("5. Wait for Windows to install (may take several minutes)")
print("6. Fonts will appear in Word, Figma, etc. immediately!")
print()
print("💡 TIPS:")
print("• If 'Install for all users' appears, choose that option")
print("• Installation may take 3-5 minutes for all fonts")
print("• You can install in batches if needed (select groups of fonts)")
print()

# Try to open the directory
try:
    os.system(f'explorer "{user_fonts}"')
    print("🔍 Fonts directory opened in File Explorer!")
except:
    print(f"🔍 Please manually open: {user_fonts}")

print()
print("✨ Ready for manual installation!")
