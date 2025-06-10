#!/usr/bin/env python3
"""
Fontshare Bulk Font Downloader - Final Working Version
Downloads all fonts from Fontshare.com using their API
"""

import asyncio
import aiohttp
import sys
import time
from pathlib import Path


def main():
    """Main function that downloads all Fontshare fonts."""
    
    print("🚀 Fontshare Bulk Font Downloader")
    print("=" * 40)
    
    # Configuration
    output_dir = Path("./fontshare_fonts")
    rate_limit = 0.5  # seconds between downloads
    
    # Font list - you can add more fonts here
    fonts = [
        "satoshi", "cabinet-grotesk", "clash-display", "general-sans",
        "switzer", "clash-grotesk", "supreme", "author", "zodiak",
        "eiko", "fraktion", "sohne", "chillax", "sentient", "tanker",
        "synonym", "boska", "melodrama", "alpino", "ranade", "sohne-mono",
        "khand", "gambetta", "erode", "clash-text", "product-sans"
    ]
    
    print(f"📋 Will download {len(fonts)} fonts")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print(f"⏱️  Rate limit: {rate_limit} seconds between downloads")
    print("-" * 50)
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Run the download
    asyncio.run(download_all_fonts(fonts, output_dir, rate_limit))


async def download_all_fonts(fonts, output_dir, rate_limit):
    """Download all fonts asynchronously."""
    
    success_count = 0
    failed_fonts = []
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        for i, font_name in enumerate(fonts, 1):
            print(f"[{i:2d}/{len(fonts)}] Downloading {font_name}...", end=" ")
            sys.stdout.flush()
            
            try:
                # Create font directory
                font_dir = output_dir / font_name
                font_dir.mkdir(exist_ok=True)
                font_file = font_dir / f"{font_name}.zip"
                
                # Skip if already downloaded
                if font_file.exists() and font_file.stat().st_size > 0:
                    print("⏭️  (already exists)")
                    success_count += 1
                    continue
                
                # Download the font
                url = f"https://api.fontshare.com/v2/fonts/download/{font_name}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save the file
                        with open(font_file, 'wb') as f:
                            f.write(content)
                        
                        size_mb = len(content) / (1024 * 1024)
                        print(f"✅ ({size_mb:.1f} MB)")
                        success_count += 1
                        
                    else:
                        print(f"❌ HTTP {response.status}")
                        failed_fonts.append(font_name)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_fonts.append(font_name)
            
            # Rate limiting - be respectful to the server
            if i < len(fonts):  # Don't wait after the last download
                await asyncio.sleep(rate_limit)
    
    # Final statistics
    duration = time.time() - start_time
    total_size = sum(
        file.stat().st_size 
        for file in output_dir.rglob("*.zip")
    ) / (1024 * 1024 * 1024)  # Convert to GB
    
    print("-" * 50)
    print("🎉 Download Complete!")
    print(f"✅ Successfully downloaded: {success_count}/{len(fonts)} fonts")
    print(f"❌ Failed downloads: {len(failed_fonts)}")
    if failed_fonts:
        print(f"   Failed fonts: {', '.join(failed_fonts)}")
    print(f"💾 Total size: {total_size:.2f} GB")
    print(f"⏱️  Total time: {duration:.1f} seconds")
    print(f"📁 Fonts saved to: {output_dir.absolute()}")
    
    print("\n📋 Usage Instructions:")
    print("1. Extract the ZIP files to use the fonts")
    print("2. Install fonts by double-clicking the font files")
    print("3. Or copy fonts to your system's font directory")
    print("\n✨ All fonts are free to use under Fontshare's license!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
