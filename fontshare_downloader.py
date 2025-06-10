"""
Fontshare Bulk Font Downloader

A tool to download all fonts from Fontshare.com using their API endpoint.
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin
import click
from tqdm.asyncio import tqdm


class FontshareDownloader:
    """Main class for discovering and downloading fonts from Fontshare."""
    
    def __init__(self, output_dir: str = "./downloads", rate_limit: float = 1.0, max_concurrent: int = 3):
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.base_url = "https://api.fontshare.com/v2"
        self.website_url = "https://www.fontshare.com"
        
        # Setup directories
        self.fonts_dir = self.output_dir / "fonts"
        self.logs_dir = self.output_dir / "logs"
        self.metadata_dir = self.output_dir / "metadata"
        
        self._setup_directories()
        self._setup_logging()
        
    def _setup_directories(self):
        """Create necessary directories."""
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
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
        
    async def discover_fonts(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Discover all available fonts from Fontshare.
        
        This method attempts multiple strategies to find fonts:
        1. Check if there's a public API endpoint for font listings
        2. Parse the main website for font data
        3. Use known font names as fallback
        """
        self.logger.info("🔍 Discovering fonts from Fontshare...")
        
        # Strategy 1: Try to find a fonts API endpoint
        fonts = await self._try_api_discovery(session)
        if fonts:
            self.logger.info(f"✅ Found {len(fonts)} fonts via API")
            return fonts
            
        # Strategy 2: Parse the website
        fonts = await self._try_website_parsing(session)
        if fonts:
            self.logger.info(f"✅ Found {len(fonts)} fonts via website parsing")
            return fonts
            
        # Strategy 3: Use known popular fonts as fallback
        self.logger.warning("⚠️  Using fallback font list")
        return self._get_fallback_fonts()
        
    async def _try_api_discovery(self, session: aiohttp.ClientSession) -> Optional[List[str]]:
        """Try to discover fonts via API endpoints."""
        api_endpoints = [
            f"{self.base_url}/fonts",
            f"{self.base_url}/fonts/list",
            "https://www.fontshare.com/api/fonts"
        ]
        
        for endpoint in api_endpoints:
            try:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Try different possible JSON structures
                        fonts = self._extract_font_names(data)
                        if fonts:
                            return fonts
            except Exception as e:
                self.logger.debug(f"API endpoint {endpoint} failed: {e}")
                
        return None
        
    async def _try_website_parsing(self, session: aiohttp.ClientSession) -> Optional[List[str]]:
        """Try to parse font names from the website."""
        try:
            async with session.get(self.website_url) as response:
                if response.status == 200:
                    html = await response.text()
                    # Look for JSON data in script tags or data attributes
                    fonts = self._parse_fonts_from_html(html)
                    return fonts
        except Exception as e:
            self.logger.debug(f"Website parsing failed: {e}")
            
        return None
        
    def _extract_font_names(self, data: Dict) -> List[str]:
        """Extract font names from API response data."""
        fonts = []
        
        # Common JSON structures to check
        possible_keys = ['fonts', 'data', 'items', 'results']
        
        for key in possible_keys:
            if key in data:
                font_data = data[key]
                if isinstance(font_data, list):
                    for font in font_data:
                        if isinstance(font, dict):
                            # Try common name fields
                            name = font.get('slug') or font.get('name') or font.get('id')
                            if name:
                                fonts.append(name.lower().replace(' ', '-'))
                        elif isinstance(font, str):
                            fonts.append(font.lower().replace(' ', '-'))
                            
        return fonts
        
    def _parse_fonts_from_html(self, html: str) -> List[str]:
        """Parse font names from HTML content."""
        import re
        
        # Look for JSON data in script tags
        json_pattern = r'(?:fonts|FONTS).*?(\[.*?\])'
        matches = re.findall(json_pattern, html, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                fonts = self._extract_font_names({'fonts': data})
                if fonts:
                    return fonts
            except json.JSONDecodeError:
                continue
                
        # Look for font names in href attributes
        href_pattern = r'href="[^"]*?/([a-z-]+)"'
        font_candidates = re.findall(href_pattern, html)
          # Filter out non-font URLs (basic heuristic)
        fonts = [name for name in font_candidates 
                if len(name) > 2 and '-' in name and not name.startswith('www')]
        
        return list(set(fonts)) if fonts else []
    
    def _get_fallback_fonts(self) -> List[str]:
        """Return a list of known Fontshare fonts as fallback."""
        try:
            from font_list import FONTSHARE_FONTS, POTENTIAL_FONTS
            
            # Start with known fonts
            all_fonts = FONTSHARE_FONTS.copy()
            
            # Test potential fonts to see which ones are available
            self.logger.info("🔍 Testing additional potential fonts...")
            available_potential = []
            
            for font in POTENTIAL_FONTS[:10]:  # Test first 10 to avoid too many requests
                if self._test_font_availability(font):
                    available_potential.append(font)
                    
            if available_potential:
                self.logger.info(f"✅ Found {len(available_potential)} additional fonts")
                all_fonts.extend(available_potential)
            
            return all_fonts
            
        except ImportError:
            # Fallback to basic list if font_list.py is not available
            return [
                "satoshi", "cabinet-grotesk", "clash-display", "general-sans",
                "switzer", "clash-grotesk", "supreme", "author", "zodiak",
                "eiko", "fraktion", "sohne", "chillax"
            ]
    
    def _test_font_availability(self, font_name: str) -> bool:
        """Test if a font is available for download."""
        try:
            import requests
            url = f"{self.base_url}/fonts/download/{font_name}"
            response = requests.head(url, timeout=3)
            return response.status_code == 200
        except:
            return False
        
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
                            
                        self.logger.info(f"✅ Downloaded {font_name} ({len(content)} bytes)")
                        
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
        
        # Save font list to metadata
        metadata_file = self.metadata_dir / "font-list.json"
        with open(metadata_file, 'w') as f:
            json.dump({
                "fonts": font_list,
                "total_count": len(font_list),
                "discovery_time": time.time()
            }, f, indent=2)
            
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
        
        async with aiohttp.ClientSession() as session:
            # Discover fonts
            font_list = await self.discover_fonts(session)
            
            if not font_list:
                self.logger.error("❌ No fonts discovered. Please check your internet connection.")
                return
                
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
    print("🚀 Fontshare Bulk Font Downloader")
    print("="*40)
    
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
