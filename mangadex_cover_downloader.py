#!/usr/bin/env python3
"""
MangaDex Cover Page Downloader

This script scans a local manga directory, searches MangaDex for each manga,
and downloads all available cover pages to a specified directory.

Author: Futs
Version: 1.0
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import logging
from urllib.parse import quote
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mangadex_cover_downloader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MangaDexCoverDownloader:
    """Main class for downloading MangaDex cover pages."""
    
    def __init__(self, manga_dir: str, cover_dir: str, delay: float = 1.0):
        self.manga_dir = Path(manga_dir)
        self.cover_dir = Path(cover_dir)
        self.delay = delay
        self.api_base = "https://api.mangadex.org"
        self.session = None
        
        # Ensure directories exist
        self.cover_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_manga': 0,
            'found_on_mangadex': 0,
            'covers_downloaded': 0,
            'errors': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'MangaDex Cover Downloader 1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def get_local_manga_list(self) -> List[str]:
        """Get list of manga directories from local storage."""
        manga_list = []
        
        if not self.manga_dir.exists():
            logger.error(f"Manga directory does not exist: {self.manga_dir}")
            return manga_list
        
        for item in self.manga_dir.iterdir():
            if item.is_dir():
                manga_list.append(item.name)
        
        logger.info(f"Found {len(manga_list)} manga directories")
        return sorted(manga_list)
    
    def clean_manga_title(self, title: str) -> str:
        """Clean manga title for better search results."""
        title = re.sub(r'^(The|A|An)\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*$', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    async def search_mangadex(self, title: str) -> Optional[Dict]:
        """Search for manga on MangaDex."""
        try:
            clean_title = self.clean_manga_title(title)
            search_url = f"{self.api_base}/manga"
            
            params = {
                'title': clean_title,
                'limit': 10,
                'includes[]': ['cover_art', 'author', 'artist'],
                'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
            }
            
            logger.info(f"Searching MangaDex for: {clean_title}")
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Search failed for '{title}': HTTP {response.status}")
                    return None
                
                data = await response.json()
                
                if not data.get('data'):
                    logger.warning(f"No results found for '{title}'")
                    return None
                
                # Return the first result (best match)
                return data['data'][0]
                
        except Exception as e:
            logger.error(f"Error searching for '{title}': {e}")
            return None
    
    async def get_manga_covers(self, manga_id: str) -> List[Dict]:
        """Get all cover art for a manga."""
        try:
            covers_url = f"{self.api_base}/cover"
            params = {
                'manga[]': manga_id,
                'limit': 100
            }
            
            async with self.session.get(covers_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Failed to get covers for manga {manga_id}: HTTP {response.status}")
                    return []
                
                data = await response.json()
                return data.get('data', [])
                
        except Exception as e:
            logger.error(f"Error getting covers for manga {manga_id}: {e}")
            return []
    
    async def download_cover(self, manga_title: str, cover_data: Dict, manga_id: str, volume: Optional[str] = None) -> bool:
        """Download a single cover image."""
        try:
            filename = cover_data['attributes']['fileName']

            # Construct cover URL
            cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"
            
            # Create manga-specific directory
            manga_cover_dir = self.cover_dir / manga_title
            manga_cover_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine filename
            if volume:
                cover_filename = f"{manga_title} - Volume {volume}.jpg"
            else:
                # Use cover ID as fallback
                cover_id = cover_data['id']
                cover_filename = f"{manga_title} - Cover {cover_id}.jpg"
            
            cover_path = manga_cover_dir / cover_filename
            
            # Skip if already exists
            if cover_path.exists():
                logger.info(f"Cover already exists: {cover_filename}")
                return True
            
            logger.info(f"Downloading cover: {cover_filename}")
            
            async with self.session.get(cover_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to download cover: HTTP {response.status}")
                    return False
                
                async with aiofiles.open(cover_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                logger.info(f"Successfully downloaded: {cover_filename}")
                return True
                
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")
            return False
    
    async def process_manga(self, manga_title: str) -> bool:
        """Process a single manga: search and download covers."""
        try:
            logger.info(f"Processing manga: {manga_title}")
            
            # Search for manga
            manga_data = await self.search_mangadex(manga_title)
            if not manga_data:
                self.stats['errors'] += 1
                return False
            
            self.stats['found_on_mangadex'] += 1
            manga_id = manga_data['id']
            
            # Get all covers
            covers = await self.get_manga_covers(manga_id)
            if not covers:
                logger.warning(f"No covers found for '{manga_title}'")
                return False
            
            logger.info(f"Found {len(covers)} covers for '{manga_title}'")
            
            # Download each cover
            success_count = 0
            for cover in covers:
                volume = cover['attributes'].get('volume')
                if await self.download_cover(manga_title, cover, manga_id, volume):
                    success_count += 1
                    self.stats['covers_downloaded'] += 1
                
                # Rate limiting
                await asyncio.sleep(self.delay)
            
            logger.info(f"Downloaded {success_count}/{len(covers)} covers for '{manga_title}'")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing manga '{manga_title}': {e}")
            self.stats['errors'] += 1
            return False
    
    async def run(self, manga_list: Optional[List[str]] = None) -> None:
        """Main execution method."""
        if manga_list is None:
            manga_list = self.get_local_manga_list()
        
        self.stats['total_manga'] = len(manga_list)
        
        logger.info(f"Starting to process {len(manga_list)} manga")
        
        for i, manga_title in enumerate(manga_list, 1):
            logger.info(f"Progress: {i}/{len(manga_list)} - {manga_title}")
            
            await self.process_manga(manga_title)
            
            # Rate limiting between manga
            if i < len(manga_list):
                await asyncio.sleep(self.delay)
        
        # Print final statistics
        self.print_stats()
    
    def print_stats(self):
        """Print download statistics."""
        logger.info("=" * 50)
        logger.info("DOWNLOAD STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total manga processed: {self.stats['total_manga']}")
        logger.info(f"Found on MangaDex: {self.stats['found_on_mangadex']}")
        logger.info(f"Covers downloaded: {self.stats['covers_downloaded']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 50)


def get_default_directories() -> Tuple[str, str]:
    """Get default source and destination directories."""
    user_home = Path.home()
    default_manga_dir = str(user_home / "Documents" / "Manga")
    default_cover_dir = str(user_home / "Documents" / "Cover-Pages")
    return default_manga_dir, default_cover_dir


def prompt_for_directory(prompt_text: str, default_path: Optional[str] = None) -> str:
    """Prompt user for a directory path."""
    while True:
        if default_path:
            user_input = input(f"{prompt_text} (default: {default_path}): ").strip()
            if not user_input:
                user_input = default_path
        else:
            user_input = input(f"{prompt_text}: ").strip()

        if not user_input:
            print("Please enter a valid directory path.")
            continue

        path = Path(user_input).expanduser().resolve()

        if prompt_text.lower().startswith("source") or "manga" in prompt_text.lower():
            # Source directory must exist
            if not path.exists():
                print(f"Directory does not exist: {path}")
                continue
            if not path.is_dir():
                print(f"Path is not a directory: {path}")
                continue
        else:
            # Destination directory - create if it doesn't exist
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {path}")
            except Exception as e:
                print(f"Cannot create directory {path}: {e}")
                continue

        return str(path)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Download MangaDex cover pages')
    parser.add_argument('--manga-dir',
                       help='Directory containing manga folders')
    parser.add_argument('--cover-dir',
                       help='Directory to save cover pages')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds')
    parser.add_argument('--manga', nargs='+',
                       help='Specific manga to process (by folder name)')
    parser.add_argument('--interactive', action='store_true',
                       help='Prompt for directories interactively')

    args = parser.parse_args()

    # Determine directories
    if args.interactive or not args.manga_dir or not args.cover_dir:
        print("MangaDex Cover Downloader")
        print("=" * 40)

        default_manga_dir, default_cover_dir = get_default_directories()

        manga_dir = args.manga_dir or prompt_for_directory(
            "Enter source directory (containing manga folders)",
            default_manga_dir
        )

        cover_dir = args.cover_dir or prompt_for_directory(
            "Enter destination directory (for cover pages)",
            default_cover_dir
        )
    else:
        manga_dir = args.manga_dir
        cover_dir = args.cover_dir

    async with MangaDexCoverDownloader(manga_dir, cover_dir, args.delay) as downloader:
        await downloader.run(args.manga)


if __name__ == "__main__":
    asyncio.run(main())
