#!/usr/bin/env python3
"""
Test script to verify MangaDex API functionality with the Bouncer Tokyo Fist example.
"""

import asyncio
import aiohttp
import json
from pathlib import Path

async def test_mangadex_api():
    """Test MangaDex API with Bouncer Tokyo Fist example."""
    
    async with aiohttp.ClientSession() as session:
        # Test search
        print("Testing MangaDex search for 'Bouncer Tokyo Fist'...")
        
        search_url = "https://api.mangadex.org/manga"
        params = {
            'title': 'Bouncer Tokyo Fist',
            'limit': 5,
            'includes[]': ['cover_art', 'author', 'artist'],
            'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
        }
        
        async with session.get(search_url, params=params) as response:
            if response.status != 200:
                print(f"Search failed: HTTP {response.status}")
                return
            
            data = await response.json()
            
            if not data.get('data'):
                print("No results found")
                return
            
            print(f"Found {len(data['data'])} results")
            
            # Get the first result
            manga = data['data'][0]
            manga_id = manga['id']
            title = manga['attributes']['title'].get('en', 'Unknown Title')
            
            print(f"First result: {title} (ID: {manga_id})")
            
            # Test getting covers
            print(f"\nGetting covers for manga ID: {manga_id}")
            
            covers_url = "https://api.mangadex.org/cover"
            cover_params = {
                'manga[]': manga_id,
                'limit': 100
            }
            
            async with session.get(covers_url, params=cover_params) as cover_response:
                if cover_response.status != 200:
                    print(f"Cover request failed: HTTP {cover_response.status}")
                    return
                
                cover_data = await cover_response.json()
                covers = cover_data.get('data', [])
                
                print(f"Found {len(covers)} covers")
                
                for i, cover in enumerate(covers):
                    filename = cover['attributes']['fileName']
                    volume = cover['attributes'].get('volume', 'Unknown')
                    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"
                    
                    print(f"  Cover {i+1}: Volume {volume} - {cover_url}")
                
                # Test downloading the first cover
                if covers:
                    first_cover = covers[0]
                    filename = first_cover['attributes']['fileName']
                    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"
                    
                    print(f"\nTesting download of first cover: {cover_url}")
                    
                    async with session.get(cover_url) as img_response:
                        if img_response.status == 200:
                            content_length = img_response.headers.get('content-length', 'Unknown')
                            content_type = img_response.headers.get('content-type', 'Unknown')
                            print(f"Download successful! Size: {content_length} bytes, Type: {content_type}")
                        else:
                            print(f"Download failed: HTTP {img_response.status}")

if __name__ == "__main__":
    asyncio.run(test_mangadex_api())
