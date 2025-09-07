# Manga Cover-Page Downloader

A Python script that scans your local manga collection and downloads all available cover pages from MangaDex.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Scans local manga directories automatically
- Searches MangaDex for each manga using the API
- Downloads all available cover art (multiple volumes/covers per manga)
- Organizes covers in manga-specific folders
- Handles rate limiting to respect MangaDex API
- Comprehensive logging and error handling
- Resume capability (skips already downloaded covers)

## Setup

1. **Configure your paths (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred paths
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage

### Method 1: Enhanced Interactive Mode (Recommended)
Run the enhanced interactive downloader with folder browser:
```bash
python interactive_downloader_enhanced.py
```
Features:
- GUI folder browser (if available) or text input
- Prompts for source and destination directories
- List all available manga
- Search for specific manga
- Select which manga to download covers for

### Method 1: Interactive (Recommended)
User-friendly interactive interface with GUI folder browser:
```bash
python interactive_downloader.py
```

### Method 2: Command Line (Advanced)

#### Download all manga covers (prompts for directories):
```bash
python mangadex_cover_downloader.py
```

#### Download single manga (prompts for directories):
```bash
python mangadex_cover_downloader.py --manga "Bouncer -Tokyo Fist-"
```

#### Download multiple specific manga:
```bash
python mangadex_cover_downloader.py --manga "Bouncer -Tokyo Fist-" "Berserk"
```

#### Use interactive prompts:
```bash
python mangadex_cover_downloader.py --interactive
```

#### Skip prompts with custom directories:
```bash
python mangadex_cover_downloader.py \
  --manga-dir "/path/to/your/manga" \
  --cover-dir "/path/to/save/covers"
```

#### Adjust rate limiting:
```bash
python mangadex_cover_downloader.py --delay 2.0
```

## Directory Structure

### Input (Manga Directory)
```
/home/user/Documents/Manga/
├── Bouncer -Tokyo Fist-/
├── Berserk/
├── One Piece/
└── ...
```

### Output (Cover Directory)
```
/home/user/Documents/Manga/Cover Pages/Manga/
├── Bouncer -Tokyo Fist-/
│   ├── Bouncer -Tokyo Fist- - Volume 1.jpg
│   ├── Bouncer -Tokyo Fist- - Volume 2.jpg
│   └── ...
├── Berserk/
│   ├── Berserk - Volume 1.jpg
│   ├── Berserk - Volume 2.jpg
│   └── ...
└── ...
```

## Command Line Options

- `--manga-dir`: Source directory containing manga folders (default: `/home/user/Documents/Manga/`)
- `--cover-dir`: Destination directory for cover pages (default: `/home/user/Documents/Manga/Cover Pages/Manga/`)
- `--delay`: Delay between API requests in seconds (default: 1.0)
- `--manga`: Specific manga to process (by folder name)

## Example

Using the "Bouncer -Tokyo Fist-" example:

1. **Source**: `/home/user/Documents/Manga/Bouncer -Tokyo Fist-/`
2. **Search**: MangaDex API search for "Bouncer Tokyo Fist"
3. **Result**: https://mangadex.org/title/5356ad15-1012-4867-af98-70478eb8d643/bouncer-tokyo-fist
4. **Covers**: Downloads all available cover art from the manga's cover gallery
5. **Output**:
   - Volume covers: `/home/user/Documents/Manga/Cover Pages/Manga/Bouncer -Tokyo Fist-/Bouncer -Tokyo Fist- - Volume 1.jpg`
   - Main cover: `/home/user/Documents/Manga/Cover Pages/Manga/Bouncer -Tokyo Fist-/Bouncer -Tokyo Fist- - Main Cover.jpg`

## Logging

The script creates a log file `mangadex_cover_downloader.log` with detailed information about:
- Search results for each manga
- Download progress
- Errors and warnings
- Final statistics

## Error Handling

- Skips manga not found on MangaDex
- Retries failed downloads
- Continues processing even if individual manga fail
- Provides detailed error logging

## Rate Limiting

The script includes built-in rate limiting to respect MangaDex's API:
- 1 second delay between requests by default
- Configurable delay via `--delay` parameter
- Separate delays for search and download operations

## Requirements

- Python 3.12+
- aiohttp
- aiofiles

## Testing

Test the MangaDex API connection:
```bash
python test_mangadex_api.py
```

This will test the API with the "Bouncer Tokyo Fist" example and show available covers.

## Default Paths

The scripts use generic default paths that work on any system:

### Default Directories
- **Source**: `~/Documents/Manga` (user's Documents/Manga folder)
- **Destination**: `~/Documents/Cover-Pages` (user's Documents/Cover-Pages folder)

### Features
- **Generic defaults**: No system-specific hardcoded paths
- **User prompting**: Always prompts for directory confirmation
- **GUI folder browser**: Optional graphical folder selection (if tkinter available)
- **Flexible input**: Browse, type path, or use defaults

All scripts automatically use these generic defaults while still allowing full customization.

## Configuration (.env file)

You can customize default paths and behavior by creating a `.env` file:

```bash
cp .env.example .env
```

### Available Settings:

- **`MANGA_SOURCE_DIR`**: Your manga collection directory
- **`COVER_DESTINATION_DIR`**: Where to save downloaded covers
- **`AUTO_USE_DEFAULTS`**: Set to `true` to skip directory prompts
- **`DOWNLOAD_DELAY`**: Delay between downloads (seconds)

### Example .env:
```env
MANGA_SOURCE_DIR=/home/username/Documents/Manga
COVER_DESTINATION_DIR=/home/username/Documents/Cover-Pages
AUTO_USE_DEFAULTS=true
DOWNLOAD_DELAY=1.0
```

With `AUTO_USE_DEFAULTS=true`, the interactive downloader will skip directory selection and use your configured paths automatically.

## Cover Types

The downloader identifies and downloads two types of covers from MangaDx:

### 📚 **Volume Covers**
- Covers tied to specific volumes
- Named: `{Manga Title} - Volume {Number}.jpg`
- Example: `"Solo Leveling - Volume 1.jpg"`

### 🎨 **Main Covers**
- General manga cover art (not tied to specific volumes)
- Named: `{Manga Title} - Main Cover.jpg`
- Example: `"Shamo - Main Cover.jpg"`
- These are the primary cover images for the manga series

Both types are valuable:
- **Volume covers** help identify specific volumes in your collection
- **Main covers** provide the primary series artwork for display/organization
