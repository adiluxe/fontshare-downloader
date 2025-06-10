"""
Quick demo of the Fontshare downloader with a few fonts
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fontshare_downloader import FontshareDownloader


async def demo_download():
    """Demo the downloader with a few fonts."""
    
    print("🚀 Fontshare Downloader Demo")
    print("=" * 30)
    
    # Create downloader with demo settings
    downloader = FontshareDownloader(
        output_dir="./demo_downloads",
        rate_limit=0.5,  # Faster for demo
        max_concurrent=2
    )
    
    # Override the font discovery to use just a few fonts for demo
    demo_fonts = ["satoshi", "cabinet-grotesk", "clash-display"]
    
    print(f"📋 Demo will download {len(demo_fonts)} fonts:")
    for i, font in enumerate(demo_fonts, 1):
        print(f"  {i}. {font}")
    
    print("\n📥 Starting download...")
    
    # Download the demo fonts
    stats = await downloader.download_all_fonts(demo_fonts)
    
    print("\n🎉 Demo Complete!")
    print(f"✅ Successfully downloaded: {stats['success']} fonts")
    print(f"❌ Failed: {stats['failed']} fonts")
    print(f"📁 Files saved to: {downloader.fonts_dir}")


if __name__ == "__main__":
    asyncio.run(demo_download())
