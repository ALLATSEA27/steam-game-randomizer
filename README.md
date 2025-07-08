# 🎲 Steam Game Randomizer

A Streamlit app that helps you discover games in your Steam library that you haven't played much. Perfect for when you can't decide what to play!

## Features

- 🎯 Randomly select games from your Steam library
- ⏱️ Filter by playtime (default: less than 2 hours)
- 🖼️ Display game images and detailed information
- 📊 Show game ratings, genres, and system requirements
- 🏆 **Achievements:** See your total and completed achievements for each game, with a progress bar (Online Mode only)
- 🔍 View comprehensive game details including DRM, languages, and pricing
- 💾 **Offline Mode** - Works without internet after initial setup
- 🗂️ **Smart Caching** - Automatically caches game data for faster loading
- 🎲 **Exclude Rolled Games** - Option to avoid repeating previously selected games
- ⚙️ **Collapsible Setup** - Clean interface with setup hidden by default

## Prerequisites

- Python 3.7 or higher
- A Steam account
- Steam API key (only needed for initial setup)
- Your SteamID64

## Installation

### Prerequisites
- Python 3.7 or higher installed on your system
- Git (optional, for cloning the repository)

### Step 1: Get the Code
**Option A: Clone the repository (if you have Git)**
```bash
git clone git@github.com:ALLATSEA27/steam-game-randomizer.git
cd steamrecommender
```

**Option B: Download and extract**
- Download the ZIP file from the repository
- Extract it to a folder on your computer
- Open terminal/command prompt and navigate to the extracted folder

### Step 2: Set Up Virtual Environment

#### On macOS/Linux:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
```

#### On Windows:
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Your prompt should now show (venv) at the beginning
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4: Run the App
```bash
streamlit run cached_app.py
```

The app will open in your default web browser at `http://localhost:8501`

### Deactivating the Virtual Environment
When you're done using the app, you can deactivate the virtual environment:
```bash
deactivate
```

## How to Get Your Steam API Key

### Step 1: Access Steam Developer Portal
1. Go to [Steam Community Developer Portal](https://steamcommunity.com/dev/apikey)
2. Sign in with your Steam account if not already signed in

### Step 2: Register for API Key
1. You'll see a page asking for your domain name
2. **For local use, enter:** `localhost` or `127.0.0.1`
3. Click **"Register"**

### Step 3: Get Your API Key
1. Your API key will be displayed (it looks like: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
2. **Important:** Keep this key private and don't share it
3. Copy the key for use in the app

## How to Find Your SteamID64

### Method 1: Using SteamID.io (Easiest)
1. Go to [SteamID.io](https://steamid.io/lookup)
2. Enter your Steam username or profile URL
3. Copy the **SteamID64** (the long number)

### Method 2: From Your Steam Profile
1. Go to your Steam profile page
2. Right-click on your profile and select "Copy Page URL"
3. The URL will look like: `https://steamcommunity.com/profiles/76561198012345678/`
4. The number at the end is your SteamID64: `76561198012345678`

### Method 3: From Steam Client
1. Open Steam
2. Go to your profile
3. Click "Edit Profile"
4. Look for "Steam ID" in the profile settings

## Usage

### Initial Setup (Online Mode)
1. **Start the app** by running `streamlit run cached_app.py`
2. **Click "⚙️ Setup & Configuration"** to expand the setup section
3. **Select "Online Mode"** to fetch fresh data
4. **Enter your Steam API key** (from the steps above)
5. **Enter your SteamID64** (from the steps above)
6. **Click "🔄 Fetch Fresh Data"** to load your game library
7. **Optionally click "📥 Download All Game Details"** to cache detailed information for offline use

### Optional: Use a .env File for Credentials

For easier and more secure local use, you can create a `.env` file in your project folder:

```
STEAM_API_KEY=your_steam_api_key_here
STEAM_ID64=your_steamid64_here
```

- The app will automatically load these values and pre-fill the input fields.
- Your `.env` file is private and should **not** be committed to git (it's in `.gitignore`).
- You can still edit the fields in the app if you want to use different credentials.

### Daily Use (Offline Mode)
1. **Select "Offline Mode"** in the setup section
2. **Enter your SteamID64** (no API key needed)
3. **Click the "🎲" button** to get a random game
4. **Adjust settings in the sidebar** as needed

### Features
- **🎯 Randomizer Settings** (in sidebar):
  - Adjust max playtime filter (0-100 hours)
  - Toggle "Exclude rolled games" to avoid repeats
- **🗂️ Cache Management** (in sidebar):
  - View cache statistics
  - Clear cache if needed
  - Reset rolled games list
  - Refresh game details (Online Mode only)

## Modes Explained

### Online Mode
- **Purpose:** Initial setup and data updates
- **Requirements:** Steam API key + SteamID64
- **Features:** 
  - Fetch fresh game data from Steam
  - Update existing cached data
  - Download all game details for offline use
  - Refresh individual game details

### Offline Mode
- **Purpose:** Daily use after initial setup
- **Requirements:** SteamID64 only
- **Features:**
  - Use cached game data (no internet required)
  - Full randomizer functionality
  - View all cached game details
  - Perfect for quick game selection

## Troubleshooting

### "No games found or profile is private"
- Make sure your Steam profile is set to public
- Verify your SteamID64 is correct
- Check that your API key is valid (Online Mode only)

### "Failed to fetch data from Steam API"
- Verify your API key is correct
- Make sure you entered `localhost` when registering for the API key
- Check your internet connection

### "No cached data found for this SteamID"
- Switch to Online Mode and fetch data first
- Make sure you've successfully downloaded your game library at least once

### "No games found with less than X hours of playtime"
- Try increasing the playtime limit using the sidebar slider
- Some games might not have playtime data if never launched
- Check if "Exclude rolled games" is filtering out too many games

### Game images not loading
- This is normal for some games - Steam doesn't have images for all games
- The app will still show all other game information

### Cache issues
- Use the sidebar cache management tools
- Clear cache and re-download if needed
- Check cache statistics for troubleshooting

## Privacy & Security

- Your Steam API key is only used locally and never stored
- Game data is cached locally on your machine
- No personal data is collected or transmitted
- The app runs entirely on your local machine
- Cache files are stored in a `cache/` folder in the app directory

## Features in Detail

### Game Information Displayed
- **Basic Info:** Name, playtime, app ID
- **Media:** Game header image with fallback options
- **Ratings:** Metacritic score, Steam recommendations count
- **Achievements:** Total and completed achievements with a progress bar (Online Mode only, if supported by the game)
- **Details:** Release date, genres, short description
- **System:** PC requirements (minimum/recommended), DRM notice, age rating
- **Support:** Languages, categories (Single-player, Multi-player, etc.)
- **Pricing:** Current price, sale information
- **Platforms:** Windows, Mac, Linux support
- **Features:** Controller support, cloud saves, family sharing, remote play
- **Links:** Direct link to Steam store page

### Filtering & Randomization
- **Playtime Filter:** Adjustable slider (0-100 hours) in sidebar
- **Exclude Rolled Games:** Toggle to avoid repeating selections
- **Session Persistence:** Rolled games tracked across sessions
- **Smart Caching:** Game data cached for 7 days, details for 30 days

### Cache Management
- **Automatic Caching:** Game lists and details cached automatically
- **Cache Statistics:** View file count and total size
- **Cache Controls:** Clear cache, refresh details, reset rolled games
- **Offline Capability:** Full functionality without internet after setup

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the app!

## License

This project is open source and available under the MIT License.

---

**Happy Gaming! 🎮** 