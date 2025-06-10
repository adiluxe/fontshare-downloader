"""
Fontshare Bulk Font Downloader - Simple Version

A streamlined tool to download all fonts from Fontshare.com using their API endpoint.
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from pathlib import Path
from typing import List, Dict
import click
from tqdm.asyncio import tqdm


class FontshareDownloader:
    """Simple and effective Fontshare font downloader."""
    
    def __init__(self, output_dir: str = "./downloads", rate_limit: float = 1.0, max_concurrent: int = 3):
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.base_url = "https://api.fontshare.com/v2"
        
        # Setup directories
        self.fonts_dir = self.output_dir / "fonts"
        self.logs_dir = self.output_dir / "logs"
        
        self._setup_directories()
        self._setup_logging()
        
    def _setup_directories(self):
        """Create necessary directories."""
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs_dir / "download.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_font_list(self) -> List[str]:
        """Get comprehensive list of Fontshare fonts."""
        try:
            from font_list import FONTSHARE_FONTS
            self.logger.info(f"📋 Loaded {len(FONTSHARE_FONTS)} known fonts from font_list.py")
            return FONTSHARE_FONTS
        except ImportError:
            self.logger.warning("⚠️  font_list.py not found, using built-in list")
            return self._get_builtin_fonts()
    
    def _get_builtin_fonts(self) -> List[str]:
        """Built-in list of known Fontshare fonts."""
        return [
            "satoshi", "cabinet-grotesk", "clash-display", "general-sans",
            "switzer", "clash-grotesk", "supreme", "author", "zodiak",
            "eiko", "fraktion", "sohne", "chillax", "sentient", "tanker",
            "synonym", "boska", "melodrama", "alpino", "ranade", "sohne-mono",
            "khand", "gambetta", "erode"
        ]
        
    async def download_font(self, session: aiohttp.ClientSession, font_name: str, semaphore: asyncio.Semaphore) -> bool:
        """Download a single font."""
        async with semaphore:
            try:
                download_url = f"{self.base_url}/fonts/download/{font_name}"
                font_dir = self.fonts_dir / font_name
                font_dir.mkdir(exist_ok=True)
                font_file = font_dir / f"{font_name}.zip"
                
                # Skip if already downloaded
                if font_file.exists() and font_file.stat().st_size > 0:
                    self.logger.info(f"⏭️  Skipping {font_name} (already downloaded)")
                    return True
                    
                async with session.get(download_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Write file
                        with open(font_file, 'wb') as f:
                            f.write(content)
                            
                        size_mb = len(content) / (1024 * 1024)
                        self.logger.info(f"✅ Downloaded {font_name} ({size_mb:.1f} MB)")
                        
                        # Rate limiting
                        await asyncio.sleep(self.rate_limit)
                        return True
                    else:
                        self.logger.error(f"❌ Failed to download {font_name}: HTTP {response.status}")
                        return False
                        
            except Exception as e:
                self.logger.error(f"❌ Error downloading {font_name}: {e}")
                return False
                
    async def download_all_fonts(self, font_list: List[str]) -> Dict[str, int]:
        """Download all fonts with progress tracking."""
        self.logger.info(f"📥 Starting download of {len(font_list)} fonts...")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for font_name in font_list:
                task = self.download_font(session, font_name, semaphore)
                tasks.append(task)
                
            # Execute with progress bar
            results = []
            for coro in tqdm.as_completed(tasks, desc="Downloading fonts"):
                result = await coro
                results.append(result)
                
        # Calculate statistics
        success_count = sum(results)
        failed_count = len(results) - success_count
        
        stats = {
            "total": len(font_list),
            "success": success_count,
            "failed": failed_count
        }
        
        self.logger.info(f"📊 Download complete! Success: {success_count}, Failed: {failed_count}")
        return stats
        
    async def run(self):
        """Main execution method."""
        start_time = time.time()
        
        print("🚀 Fontshare Bulk Font Downloader")
        print("=" * 40)
        
        # Get font list
        font_list = self.get_font_list()
        print(f"📋 Found {len(font_list)} fonts to download")
        
        # Download fonts
        stats = await self.download_all_fonts(font_list)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("🎉 Fontshare Bulk Download Complete!")
        print("="*50)
        print(f"📁 Fonts saved to: {self.fonts_dir}")
        print(f"📊 Success: {stats['success']} fonts")
        print(f"❌ Failed: {stats['failed']} fonts")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"📋 Logs saved to: {self.logs_dir / 'download.log'}")


@click.command()
@click.option('--output-dir', '-o', default='./downloads', help='Output directory for downloads')
@click.option('--rate-limit', '-r', default=1.0, help='Delay between requests in seconds')
@click.option('--max-concurrent', '-c', default=3, help='Maximum concurrent downloads')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(output_dir, rate_limit, max_concurrent, verbose):
    """
    Fontshare Bulk Font Downloader
    
    Downloads all available fonts from Fontshare.com using their API.
    """
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    downloader = FontshareDownloader(
        output_dir=output_dir,
        rate_limit=rate_limit,
        max_concurrent=max_concurrent
    )
    
    try:
        asyncio.run(downloader.run())
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Unexpected error occurred")


if __name__ == "__main__":
    main()
