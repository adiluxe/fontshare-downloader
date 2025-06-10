#!/usr/bin/env python3
"""
Simple Fontshare Font Downloader
Downloads fonts from Fontshare.com using their API
"""

import asyncio
import aiohttp
import os
import time
from pathlib import Path


class SimpleFontshareDownloader:
    def __init__(self, output_dir="./downloads"):
        self.output_dir = Path(output_dir)
        self.fonts_dir = self.output_dir / "fonts"
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        
    def get_font_list(self):
        """Get list of fonts to download."""
        # Import the font list if available, otherwise use built-in
        try:
            from font_list import FONTSHARE_FONTS
            return FONTSHARE_FONTS
        except ImportError:
            return [
                "satoshi", "cabinet-grotesk", "clash-display", "general-sans",
                "switzer", "clash-grotesk", "supreme", "author", "zodiak",
                "eiko", "fraktion", "sohne", "chillax", "sentient", "tanker",
                "synonym", "boska", "melodrama", "alpino", "ranade"
            ]
    
    async def download_font(self, session, font_name):
        """Download a single font."""
        try:
            url = f"https://api.fontshare.com/v2/fonts/download/{font_name}"
            font_dir = self.fonts_dir / font_name
            font_dir.mkdir(exist_ok=True)
            font_file = font_dir / f"{font_name}.zip"
            
            # Skip if already exists
            if font_file.exists() and font_file.stat().st_size > 0:
                print(f"⏭️  {font_name} already downloaded")
                return True
            
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(font_file, 'wb') as f:
                        f.write(content)
                    
                    size_mb = len(content) / (1024 * 1024)
                    print(f"✅ {font_name} downloaded ({size_mb:.1f} MB)")
                    return True
                else:
                    print(f"❌ {font_name} failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ {font_name} error: {e}")
            return False
    
    async def download_all(self):
        """Download all fonts."""
        fonts = self.get_font_list()
        print(f"🚀 Downloading {len(fonts)} fonts from Fontshare")
        print(f"📁 Output directory: {self.fonts_dir}")
        print("-" * 50)
        
        success_count = 0
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            for i, font in enumerate(fonts, 1):
                print(f"[{i}/{len(fonts)}] Downloading {font}...")
                result = await self.download_font(session, font)
                if result:
                    success_count += 1
                
                # Small delay to be respectful
                await asyncio.sleep(0.5)
        
        duration = time.time() - start_time
        
        print("-" * 50)
        print(f"🎉 Download complete!")
        print(f"✅ Successfully downloaded: {success_count}/{len(fonts)} fonts")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"📁 Fonts saved to: {self.fonts_dir}")


async def main():
    """Main function."""
    downloader = SimpleFontshareDownloader()
    await downloader.download_all()


if __name__ == "__main__":
    print("🚀 Simple Fontshare Downloader")
    print("==============================")
    asyncio.run(main())
