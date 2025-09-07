#!/usr/bin/env python3
"""
Enhanced Interactive MangaDex Cover Downloader with Generic Default Paths

Features:
- GUI folder browser (if available)
- Interactive manga selection
- Batch operations
- Generic default paths
"""

import asyncio
from pathlib import Path
from typing import Optional
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
from mangadex_cover_downloader import MangaDexCoverDownloader, prompt_for_directory, get_default_directories

def browse_for_folder(title: str, initial_dir: Optional[str] = None) -> str:
    """Open a GUI folder browser dialog."""
    if not HAS_TKINTER:
        raise ImportError("tkinter not available")
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(
        title=title,
        initialdir=initial_dir
    )
    
    root.destroy()
    return folder_path

def get_directory_with_options(prompt: str, default_path: str) -> str:
    """Get directory with GUI/text/default options."""
    print(f"\n{prompt}")
    
    if HAS_TKINTER:
        print("Choose: (b)rowse with GUI, (t)ype path, or (d)efault")
        choice = input("Your choice [b/t/d]: ").lower().strip()
    else:
        print("Choose: (t)ype path or (d)efault")
        choice = input("Your choice [t/d]: ").lower().strip()
    
    if choice == 'b' and HAS_TKINTER:
        try:
            folder = browse_for_folder(prompt, default_path)
            if folder:
                return folder
            else:
                print("No folder selected, using default.")
                return default_path
        except Exception as e:
            print(f"GUI browser failed: {e}")
            print("Falling back to text input...")
            choice = 't'
    
    if choice == 't':
        path = input(f"Enter path (default: {default_path}): ").strip()
        return path if path else default_path
    else:
        return default_path

def list_available_manga(manga_dir: str) -> list:
    """List all available manga in the directory."""
    manga_path = Path(manga_dir)
    if not manga_path.exists():
        return []
    
    manga_list = []
    for item in manga_path.iterdir():
        if item.is_dir():
            manga_list.append(item.name)
    
    return sorted(manga_list)

def search_manga(manga_list: list, search_term: str) -> list:
    """Search for manga containing the search term."""
    search_term = search_term.lower()
    return [manga for manga in manga_list if search_term in manga.lower()]

async def main():
    print("=" * 60)
    print("Enhanced Interactive MangaDex Cover Downloader")
    print("=" * 60)
    
    if HAS_TKINTER:
        print("✓ GUI folder browser available")
    else:
        print("⚠ GUI folder browser not available (tkinter missing)")
    
    print("=" * 60)
    print("Directory Selection")
    print("=" * 60)
    
    # Get default directories
    default_manga_dir, default_cover_dir = get_default_directories()
    
    # Get directories with options
    manga_dir = get_directory_with_options(
        "1. Select source directory (containing manga folders)",
        default_manga_dir
    )
    print(f"Selected source: {manga_dir}")
    
    cover_dir = get_directory_with_options(
        "2. Select destination directory (for cover pages)",
        default_cover_dir
    )
    print(f"Selected destination: {cover_dir}")
    
    print("\nScanning manga directory...")
    manga_list = list_available_manga(manga_dir)
    
    if not manga_list:
        print(f"❌ No manga found in {manga_dir}")
        return
    
    print(f"✓ Found {len(manga_list)} manga")
    
    while True:
        print("\n" + "=" * 60)
        print("Options:")
        print("1. List all manga")
        print("2. Search manga")
        print("3. Download covers for specific manga")
        print("4. Download covers for all manga")
        print("5. Change directories")
        print("6. Quit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print(f"\nAll manga ({len(manga_list)}):")
            for i, manga in enumerate(manga_list, 1):
                print(f"{i:3d}. {manga}")
        
        elif choice == '2':
            search_term = input("Enter search term: ").strip()
            if search_term:
                results = search_manga(manga_list, search_term)
                if results:
                    print(f"\nSearch results for '{search_term}' ({len(results)}):")
                    for i, manga in enumerate(results, 1):
                        print(f"{i:3d}. {manga}")
                else:
                    print(f"No manga found matching '{search_term}'")
        
        elif choice == '3':
            manga_name = input("Enter manga name: ").strip()
            if manga_name:
                if manga_name in manga_list:
                    print(f"\nDownloading covers for: {manga_name}")
                    async with MangaDexCoverDownloader(manga_dir, cover_dir) as downloader:
                        await downloader.download_manga_covers([manga_name])
                else:
                    print(f"❌ '{manga_name}' not found in manga directory")
                    similar = search_manga(manga_list, manga_name)
                    if similar:
                        print("Did you mean one of these?")
                        for manga in similar[:5]:
                            print(f"  - {manga}")
        
        elif choice == '4':
            confirm = input(f"Download covers for all {len(manga_list)} manga? (y/N): ").strip().lower()
            if confirm == 'y':
                print(f"\nDownloading covers for all {len(manga_list)} manga...")
                async with MangaDexCoverDownloader(manga_dir, cover_dir) as downloader:
                    await downloader.download_manga_covers(manga_list)
        
        elif choice == '5':
            manga_dir = get_directory_with_options(
                "Select new source directory (containing manga folders)",
                manga_dir
            )
            cover_dir = get_directory_with_options(
                "Select new destination directory (for cover pages)",
                cover_dir
            )
            print("\nScanning new manga directory...")
            manga_list = list_available_manga(manga_dir)
            print(f"✓ Found {len(manga_list)} manga")
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
