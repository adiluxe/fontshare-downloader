#!/bin/bash

# Simple font extraction script
echo "🎨 Extracting all fonts for manual installation..."

USER_FONTS="C:/Users/exequel/AppData/Local/Microsoft/Windows/Fonts"
DOWNLOADS_DIR="downloads/fonts"

# Create user fonts directory
mkdir -p "$USER_FONTS"

# Clear existing fonts
echo "🧹 Clearing existing fonts..."
rm -f "$USER_FONTS"/*.ttf "$USER_FONTS"/*.otf 2>/dev/null

echo "📦 Extracting fonts from ZIP files..."

total_fonts=0

# Process each ZIP file
for zip_file in $(find "$DOWNLOADS_DIR" -name "*.zip"); do
    font_name=$(basename "$zip_file" .zip)
    echo "Processing: $font_name"
    
    # Extract to temp directory
    temp_dir=$(mktemp -d)
    unzip -q "$zip_file" -d "$temp_dir" 2>/dev/null
    
    # Copy font files to user fonts directory
    if find "$temp_dir" -name "*.ttf" -o -name "*.otf" | head -1 > /dev/null; then
        font_count=$(find "$temp_dir" -name "*.ttf" -o -name "*.otf" | wc -l)
        find "$temp_dir" -name "*.ttf" -o -name "*.otf" -exec cp {} "$USER_FONTS/" \;
        echo "  ✅ Extracted $font_count fonts"
        total_fonts=$((total_fonts + font_count))
    else
        echo "  ⚠️  No font files found"
    fi
    
    # Clean up temp directory
    rm -rf "$temp_dir"
done

echo ""
echo "=" * 60
echo "🎉 EXTRACTION COMPLETE!"
echo "=" * 60
echo "📝 Total fonts extracted: $total_fonts"
echo "📁 Location: $USER_FONTS"
echo ""
echo "🎯 MANUAL INSTALLATION STEPS:"
echo "1. Open File Explorer"
echo "2. Navigate to: $USER_FONTS"
echo "3. Press Ctrl+A to select ALL fonts"
echo "4. Right-click and choose 'Install' or 'Install for all users'"
echo "5. Wait for installation to complete"
echo ""
echo "🔍 Opening fonts directory..."

# Open the directory in Windows Explorer
explorer.exe "$(cygpath -w "$USER_FONTS")" 2>/dev/null || explorer.exe "$USER_FONTS" 2>/dev/null || echo "Please manually open: $USER_FONTS"

echo "✅ Ready for manual installation!"
