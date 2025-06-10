#!/usr/bin/env python3
"""
Debug version of the Fontshare downloader
"""

import asyncio
import aiohttp
import os
import time
from pathlib import Path
import sys


def log_message(message):
    """Log message to both console and file."""
    print(message, flush=True)
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


class DebugFontshareDownloader:
    def __init__(self, output_dir="./downloads"):
        self.output_dir = Path(output_dir)
        self.fonts_dir = self.output_dir / "fonts"
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        log_message(f"Initialized downloader with output dir: {self.fonts_dir}")
        
    def get_font_list(self):
        """Get list of fonts to download."""
        try:
            from font_list import FONTSHARE_FONTS
            log_message(f"Loaded {len(FONTSHARE_FONTS)} fonts from font_list.py")
            return FONTSHARE_FONTS[:5]  # Only first 5 for testing
        except ImportError:
            fonts = [
                "satoshi", "cabinet-grotesk", "clash-display", "general-sans", "switzer"
            ]
            log_message(f"Using built-in font list: {fonts}")
            return fonts
    
    async def download_font(self, session, font_name):
        """Download a single font."""
        try:
            log_message(f"Starting download for: {font_name}")
            url = f"https://api.fontshare.com/v2/fonts/download/{font_name}"
            font_dir = self.fonts_dir / font_name
            font_dir.mkdir(exist_ok=True)
            font_file = font_dir / f"{font_name}.zip"
            
            # Skip if already exists
            if font_file.exists() and font_file.stat().st_size > 0:
                log_message(f"⏭️  {font_name} already downloaded")
                return True
            
            log_message(f"Making request to: {url}")
            async with session.get(url) as response:
                log_message(f"Response status for {font_name}: {response.status}")
                if response.status == 200:
                    content = await response.read()
                    with open(font_file, 'wb') as f:
                        f.write(content)
                    
                    size_mb = len(content) / (1024 * 1024)
                    log_message(f"✅ {font_name} downloaded ({size_mb:.1f} MB)")
                    return True
                else:
                    log_message(f"❌ {font_name} failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            log_message(f"❌ {font_name} error: {e}")
            import traceback
            log_message(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def download_all(self):
        """Download all fonts."""
        log_message("Starting download_all method")
        fonts = self.get_font_list()
        log_message(f"🚀 Downloading {len(fonts)} fonts from Fontshare")
        log_message(f"📁 Output directory: {self.fonts_dir}")
        log_message("-" * 50)
        
        success_count = 0
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                log_message("Created aiohttp session")
                for i, font in enumerate(fonts, 1):
                    log_message(f"[{i}/{len(fonts)}] Processing {font}...")
                    result = await self.download_font(session, font)
                    if result:
                        success_count += 1
                    
                    # Small delay to be respectful
                    await asyncio.sleep(0.5)
        except Exception as e:
            log_message(f"Error in download_all: {e}")
            import traceback
            log_message(f"Traceback: {traceback.format_exc()}")
        
        duration = time.time() - start_time
        
        log_message("-" * 50)
        log_message(f"🎉 Download complete!")
        log_message(f"✅ Successfully downloaded: {success_count}/{len(fonts)} fonts")
        log_message(f"⏱️  Total time: {duration:.1f} seconds")
        log_message(f"📁 Fonts saved to: {self.fonts_dir}")


async def main():
    """Main function."""
    log_message("Starting main function")
    try:
        downloader = DebugFontshareDownloader()
        await downloader.download_all()
        log_message("Main function completed successfully")
    except Exception as e:
        log_message(f"Error in main: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    # Clear debug log
    with open("debug.log", "w") as f:
        f.write("Debug log started\n")
    
    log_message("🚀 Debug Fontshare Downloader")
    log_message("===============================")
    log_message(f"Python version: {sys.version}")
    log_message(f"Working directory: {os.getcwd()}")
    
    try:
        asyncio.run(main())
    except Exception as e:
        log_message(f"Top-level error: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
    
    log_message("Script finished")
