import streamlit as st
import requests
import random
import json
import re
import os
import pickle
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# --- Helper functions ---
def get_owned_games(api_key, steamid):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "include_appinfo": True,
        "include_played_free_games": True
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from Steam API.")
    data = response.json()
    if 'response' not in data or 'games' not in data['response']:
        raise Exception("No games found or profile is private.")
    return data['response']['games']

def get_game_details(app_id):
    """Get additional game details from Steam Store API"""
    try:
        url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": app_id}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']
    except Exception as e:
        st.warning(f"Could not fetch additional details: {e}")
    return None

def save_cache_data(games, steamid):
    """Save games data to local cache"""
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    cache_file = os.path.join(cache_dir, f"games_{steamid}.pkl")
    cache_data = {
        'games': games,
        'timestamp': datetime.now(),
        'steamid': steamid
    }
    
    with open(cache_file, 'wb') as f:
        pickle.dump(cache_data, f)
    
    st.success(f"Game data cached locally for offline use!")

def load_cache_data(steamid):
    """Load games data from local cache"""
    cache_file = os.path.join("cache", f"games_{steamid}.pkl")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is less than 7 days old
        if datetime.now() - cache_data['timestamp'] < timedelta(days=7):
            return cache_data['games'], cache_data['timestamp']
        else:
            st.warning("Cache is older than 7 days. Consider refreshing.")
            return cache_data['games'], cache_data['timestamp']
    
    return None, None

def save_game_details_cache(game_details, app_id):
    """Save individual game details to cache"""
    cache_dir = "cache/game_details"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    cache_file = os.path.join(cache_dir, f"game_{app_id}.pkl")
    cache_data = {
        'details': game_details,
        'timestamp': datetime.now(),
        'app_id': app_id
    }
    
    with open(cache_file, 'wb') as f:
        pickle.dump(cache_data, f)

def load_game_details_cache(app_id):
    """Load individual game details from cache"""
    cache_file = os.path.join("cache/game_details", f"game_{app_id}.pkl")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is less than 30 days old
        if datetime.now() - cache_data['timestamp'] < timedelta(days=30):
            return cache_data['details']
    
    return None

# Filter helpers
def filter_games_by_playtime(games, max_hours):
    """Filter games with less than max_hours of playtime"""
    filtered_games = []
    for game in games:
        playtime_minutes = game.get('playtime_forever', 0)
        playtime_hours = playtime_minutes / 60
        if playtime_hours < max_hours:
            filtered_games.append(game)
    return filtered_games

def get_available_genres(games):
    """Get all available genres from cached game details"""
    genres = set()
    for game in games:
        app_id = game.get('appid')
        if app_id:
            game_details = load_game_details_cache(app_id)
            if game_details and 'genres' in game_details:
                for genre in game_details['genres']:
                    genres.add(genre['description'])
    return sorted(list(genres))

def filter_games_by_genre(games, selected_genre):
    """Filter games by selected genre"""
    if selected_genre == "All Genres":
        return games
    
    filtered_games = []
    for game in games:
        app_id = game.get('appid')
        if app_id:
            game_details = load_game_details_cache(app_id)
            if game_details and 'genres' in game_details:
                game_genres = [genre['description'] for genre in game_details['genres']]
                if selected_genre in game_genres:
                    filtered_games.append(game)
    return filtered_games

def get_game_image_url(app_id):
    """Get game header image URL"""
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

def get_game_banner_url(app_id):
    """Get game banner image URL (using header for faster loading)"""
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

def clean_html_text(html_text):
    """Clean HTML tags from text"""
    if not html_text:
        return ""
    # Remove HTML tags
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    
    # Clean up the text properly
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common formatting issues
    # Remove duplicate section headers
    text = re.sub(r'(Minimum:|Recommended:|Optimal:)\s*\1', r'\1', text)
    
    # Fix broken words and spacing
    text = re.sub(r'([A-Z])\s+([A-Z])', r'\1\2', text)  # Fix "G H z" -> "GHz"
    text = re.sub(r'([a-z])\s+([A-Z])', r'\1 \2', text)  # Fix "M emory" -> "Memory"
    text = re.sub(r'([0-9])\s+([A-Z])', r'\1\2', text)  # Fix "1 G B" -> "1GB"
    text = re.sub(r'([0-9])\s+([a-z])', r'\1\2', text)  # Fix "2 . 2" -> "2.2"
    
    # Add proper line breaks for requirements
    text = re.sub(r'(OS|Processor|Memory|Graphics|Storage|DirectX|Network|Sound|Additional):', r'\n\1:', text)
    
    # Clean up multiple line breaks and spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def get_achievement_schema(api_key, app_id):
    """Fetch the achievement schema for a game (list of all achievements)"""
    url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    params = {"key": api_key, "appid": app_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            achievements = data.get("game", {}).get("availableGameStats", {}).get("achievements", [])
            return achievements
    except Exception as e:
        st.warning(f"Could not fetch achievement schema: {e}")
    return None

def get_player_achievements(api_key, steamid, app_id):
    """Fetch the player's unlocked achievements for a game"""
    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
    params = {"key": api_key, "steamid": steamid, "appid": app_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            achievements = data.get("playerstats", {}).get("achievements", [])
            return achievements
    except Exception as e:
        st.warning(f"Could not fetch player achievements: {e}")
    return None

# --- Streamlit App ---
st.set_page_config(
    page_title="Steam Game Randomizer (Offline)", 
    page_icon="🎲", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add CSS for mobile responsiveness and sidebar control
st.markdown("""
<style>
    /* Hide sidebar by default on mobile */
    @media (max-width: 768px) {
        .css-1d391kg {
            display: none !important;
        }
        .css-1d391kg.e1fqkh3o1 {
            display: none !important;
        }
        /* Ensure main content takes full width on mobile */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
    }
    
    /* Improve button sizing on mobile */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.2rem !important;
        }
    }
    
    /* Better text sizing on mobile */
    @media (max-width: 768px) {
        .stMarkdown {
            font-size: 0.9rem !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
    }
    
    /* Improve column layout on mobile */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        .row-widget.stHorizontal > div {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'games' not in st.session_state:
    st.session_state.games = None

if 'rolled_games' not in st.session_state:
    st.session_state.rolled_games = set()

if 'exclude_rolled' not in st.session_state:
    st.session_state.exclude_rolled = False

if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None

if 'show_cache_sidebar' not in st.session_state:
    st.session_state.show_cache_sidebar = False

# Main content
st.title("🎲 Steam Game Randomizer (Offline Mode)")

# Add banner image if we have a selected game
if 'selected_game' in st.session_state and st.session_state.selected_game:
    app_id = st.session_state.selected_game.get('appid')
    if app_id:
        try:
            banner_url = get_game_banner_url(app_id)
            st.image(banner_url, use_container_width=True)
        except:
            st.info("🎮 Game image not available")
            if 'mode' in locals() and mode == "Offline Mode":
                st.warning("Game images are only available in Online Mode.")

# Collapsible setup section
with st.expander("⚙️ Setup & Configuration", expanded=False):
    st.markdown("""
    This version can work offline after initial setup!

    **Online Mode:** Fetch fresh data from Steam

    **Offline Mode:** Use cached data (no internet required)

    [How to get your Steam API key?](https://steamcommunity.com/dev/apikey)

    [How to find your SteamID64?](https://steamid.io/lookup)
    """)

    # Mode selection
    mode = st.radio("Select Mode:", ["Offline Mode", "Online Mode"])

    # Get env vars
    env_api_key = os.environ.get("STEAM_API_KEY", "")
    env_steamid = os.environ.get("STEAM_ID64", "")

    # API key input (only for Online Mode)
    if mode == "Online Mode":
        api_key = st.text_input("Steam API Key", type="password", value=env_api_key)
    else:
        api_key = None
        
    # SteamID input (needed for both modes)
    steamid = st.text_input("SteamID64", value=env_steamid)

    # After steamid is set, handle Offline Mode cache loading
    if mode == "Offline Mode" and steamid:
        cached_games, cache_timestamp = load_cache_data(steamid)
        if cached_games:
            st.session_state.games = cached_games
        else:
            st.session_state.games = None
            st.error("No cached data found for this SteamID. Please switch to Online Mode and fetch your library at least once.")

    # Note about sidebar
    st.info("💡 **Tip:** Use the sidebar for cache management")
    
    # Mobile note
    st.info("📱 **Mobile users:** Tap the ☰ menu in the top-left to access sidebar controls")
    
    # Rate limiting disclaimer (only show in Online Mode)
    if mode == "Online Mode":
        st.warning("""
        ⚠️ **Steam API Rate Limits:** 
        Steam has rate limits on their API. If you encounter errors during bulk operations, 
        wait a few minutes before trying again. The app will automatically handle individual 
        game detail requests safely.
        """)

    # Show game count if games are loaded
    if st.session_state.games:
        filtered_games = filter_games_by_playtime(st.session_state.games, 2.0)  # Default 2 hours
        st.success(f"✅ Found {len(filtered_games)} games with less than 2.0 hours of playtime")

    if steamid and api_key:
        if mode == "Online Mode":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                fetch_games = st.button("🔄 Fetch Fresh Data", type="primary")
            with col2:
                update_existing = st.button("📥 Update Existing Data")
            with col3:
                download_all_details = st.button("📥 Download All Game Details")
            with col4:
                download_all_details_achievements = st.button("🏆📥 Download All Game Details & Achievements")
            
            if fetch_games:
                with st.spinner("Fetching fresh data from Steam..."):
                    try:
                        games = get_owned_games(api_key, steamid)
                        st.session_state.games = games
                        st.success(f"Found {len(games)} games in your library!")
                        
                        # Cache the data for offline use
                        save_cache_data(games, steamid)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            elif update_existing and st.session_state.games:
                with st.spinner("Updating existing data..."):
                    try:
                        # Get fresh data
                        fresh_games = get_owned_games(api_key, steamid)
                        
                        # Update playtime for existing games
                        updated_count = 0
                        for fresh_game in fresh_games:
                            for existing_game in st.session_state.games:
                                if existing_game['appid'] == fresh_game['appid']:
                                    existing_game['playtime_forever'] = fresh_game['playtime_forever']
                                    updated_count += 1
                                    break
                        
                        # Add new games
                        existing_appids = {game['appid'] for game in st.session_state.games}
                        new_games = [game for game in fresh_games if game['appid'] not in existing_appids]
                        st.session_state.games.extend(new_games)
                        
                        st.success(f"Updated {updated_count} existing games, added {len(new_games)} new games!")
                        
                        # Update cache
                        save_cache_data(st.session_state.games, steamid)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            elif download_all_details and st.session_state.games:
                st.warning("⚠️ **Note:** This operation may take several minutes and could hit Steam's rate limits. If it fails, wait a few minutes and try again.")
                with st.spinner("Downloading all game details (this may take a while)..."):
                    try:
                        total_games = len(st.session_state.games)
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        downloaded_count = 0
                        failed_count = 0
                        
                        for i, game in enumerate(st.session_state.games):
                            app_id = game.get('appid')
                            if app_id:
                                status_text.text(f"Downloading details for: {game['name']} ({i+1}/{total_games})")
                                
                                # Check if already cached
                                existing_details = load_game_details_cache(app_id)
                                if existing_details is None:
                                    # Download new details
                                    game_details = get_game_details(app_id)
                                    if game_details:
                                        save_game_details_cache(game_details, app_id)
                                        downloaded_count += 1
                                    else:
                                        failed_count += 1
                                else:
                                    downloaded_count += 1  # Already cached
                                
                                # Update progress
                                progress = (i + 1) / total_games
                                progress_bar.progress(progress)
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if failed_count > 0:
                            st.warning(f"Downloaded {downloaded_count} game details, {failed_count} failed")
                        else:
                            st.success(f"Successfully downloaded/cached {downloaded_count} game details!")
                        
                    except Exception as e:
                        st.error(f"Error during bulk download: {e}")

            elif download_all_details_achievements and st.session_state.games:
                st.warning("⚠️ **Note:** This operation may take several minutes and could hit Steam's rate limits. If it fails, wait a few minutes and try again.")
                with st.spinner("Downloading all game details and achievements (this may take a while)..."):
                    try:
                        total_games = len(st.session_state.games)
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        downloaded_count = 0
                        failed_count = 0
                        achievements_count = 0
                        for i, game in enumerate(st.session_state.games):
                            app_id = game.get('appid')
                            if app_id:
                                status_text.text(f"Downloading details for: {game['name']} ({i+1}/{total_games})")
                                # Game details
                                existing_details = load_game_details_cache(app_id)
                                if existing_details is None:
                                    game_details = get_game_details(app_id)
                                    if game_details:
                                        save_game_details_cache(game_details, app_id)
                                        downloaded_count += 1
                                    else:
                                        failed_count += 1
                                else:
                                    downloaded_count += 1  # Already cached
                                # Achievements schema
                                achievements_schema_file = os.path.join("cache/game_details", f"game_{app_id}_achievements.pkl")
                                if not os.path.exists(achievements_schema_file):
                                    schema = get_achievement_schema(api_key, app_id)
                                    if schema:
                                        with open(achievements_schema_file, 'wb') as f:
                                            pickle.dump(schema, f)
                                        achievements_count += 1
                                else:
                                    achievements_count += 1  # Already cached
                                # Player achievement progress (new)
                                player_achievements_file = os.path.join("cache/game_details", f"game_{app_id}_player_achievements.pkl")
                                if not os.path.exists(player_achievements_file):
                                    player_achievements = get_player_achievements(api_key, steamid, app_id)
                                    if player_achievements:
                                        with open(player_achievements_file, 'wb') as f:
                                            pickle.dump(player_achievements, f)
                                # Update progress
                                progress = (i + 1) / total_games
                                progress_bar.progress(progress)
                        progress_bar.empty()
                        status_text.empty()
                        st.success(f"Downloaded/cached {downloaded_count} game details, {achievements_count} achievements schemas. {failed_count} failed.")
                    except Exception as e:
                        st.error(f"Error during bulk download: {e}")

        elif mode == "Offline Mode":
            if steamid:
                cached_games, cache_timestamp = load_cache_data(steamid)
                
                if cached_games:
                    st.session_state.games = cached_games
                    # Status shown in sidebar, no need for main screen messages
                else:
                    st.error("No cached data found for this SteamID. Switch to Online Mode to fetch data first.")

    # Debug: Show available genres (simple text display)
    if st.session_state.games:
        available_genres = get_available_genres(st.session_state.games)
        if available_genres:
            st.markdown("**🔍 Available Genres in Your Library:**")
            genre_text = ", ".join(available_genres)
            st.write(f"{genre_text}")
            st.write(f"**Total:** {len(available_genres)} unique genres")
        else:
            st.info("No genre data found. Use Online Mode and download game details to see genres.")


# Randomizer section
if st.session_state.games:
    st.markdown("---")
    st.subheader("🎲 Randomizer")
    
    # Configuration in sidebar
    with st.sidebar:
        st.markdown("**🎯 Randomizer Settings:**")
        max_hours = st.slider("Max playtime (hours)", 0.0, 100.0, 2.0, 0.5, key="sidebar_max_hours")
        exclude_rolled = st.checkbox("Exclude rolled games", value=st.session_state.exclude_rolled)
        st.session_state.exclude_rolled = exclude_rolled
        
        # Genre filter
        st.markdown("**🎭 Genre Filter:**")
        available_genres = get_available_genres(st.session_state.games)
        if available_genres:
            selected_genre = st.selectbox("Select Genre:", ["All Genres"] + available_genres, key="genre_filter")
        else:
            selected_genre = "All Genres"
            st.info("No genre data available. Use Online Mode to download game details.")
    
    # Filter games by playtime
    filtered_games = filter_games_by_playtime(st.session_state.games, max_hours)
    
    # Filter by genre
    filtered_games = filter_games_by_genre(filtered_games, selected_genre)
    
    # Filter out previously rolled games if option is enabled
    if exclude_rolled and st.session_state.rolled_games:
        available_games = [game for game in filtered_games if game['appid'] not in st.session_state.rolled_games]
        excluded_count = len(filtered_games) - len(available_games)
        if excluded_count > 0:
            st.info(f"Excluded {excluded_count} previously rolled games")
        filtered_games = available_games
    
    if filtered_games:
        # Show current filter status
        filter_info = f"🎯 **{len(filtered_games)} games available**"
        if selected_genre != "All Genres":
            filter_info += f" in **{selected_genre}** genre"
        filter_info += f" with **< {max_hours} hours** playtime"
        st.info(filter_info)
        
        # Randomizer button - prominent placement
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            roll_button = st.button("🎲", type="primary", use_container_width=True)
        
        # Handle button click outside the column to avoid scope issues
        if roll_button:
            selected_game = random.choice(filtered_games)
            playtime_hours = selected_game.get('playtime_forever', 0) / 60
            app_id = selected_game.get('appid')
            
            # Add to rolled games set
            st.session_state.rolled_games.add(app_id)
            
            # Store selected game in session state for banner display
            st.session_state.selected_game = selected_game
            
            st.markdown("---")
            st.subheader("🎯 Your Random Game:")
            
            # Get additional game details (try cache first, then online)
            game_details = None
            if app_id:
                # Try to load from cache first
                game_details = load_game_details_cache(app_id)
                
                if game_details is None and mode == "Online Mode":
                    # If not in cache and online mode, fetch from Steam
                    with st.spinner("Fetching game details..."):
                        game_details = get_game_details(app_id)
                        if game_details:
                            save_game_details_cache(game_details, app_id)
                elif game_details is None and mode == "Offline Mode":
                    st.info("Game details not available offline. Use Online Mode to cache details.")
            
            # Display game info in columns
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Game image with loading optimization
                if app_id:
                    image_loaded = False
                    try:
                        image_url = get_game_image_url(app_id)
                        st.image(image_url, caption=selected_game['name'], use_container_width=True)
                        image_loaded = True
                    except:
                        # Try alternative image if header fails
                        try:
                            alt_image_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/capsule_184x69.jpg"
                            st.image(alt_image_url, caption=selected_game['name'], use_container_width=True)
                            image_loaded = True
                        except:
                            st.info("🖼️ Game image not available")
                            if 'mode' in locals() and mode == "Offline Mode":
                                st.warning("Game images are only available in Online Mode.")
                    
                    if not image_loaded:
                        st.info("🖼️ Game image not available")
                        if 'mode' in locals() and mode == "Offline Mode":
                            st.warning("Game images are only available in Online Mode.")
                
            with col2:
                st.markdown(f"### {selected_game['name']}")
                st.write(f"**Playtime:** {playtime_hours:.1f} hours")
                st.write(f"**App ID:** {app_id or 'N/A'}")
                
                # Additional details if available
                if game_details:
                    # Release date
                    if 'release_date' in game_details and game_details['release_date'].get('date'):
                        st.write(f"**Release Date:** {game_details['release_date']['date']}")
                    
                    # Genres
                    if 'genres' in game_details:
                        genres = [genre['description'] for genre in game_details['genres']]
                        st.write(f"**Genres:** {', '.join(genres[:3])}")  # Show first 3 genres
                    
                    # Metacritic score
                    if 'metacritic' in game_details and game_details['metacritic'].get('score'):
                        score = game_details['metacritic']['score']
                        st.write(f"**Metacritic Score:** {score}/100")
                    
                    # Achievements display (only in Online Mode, with API key and SteamID)
                    if app_id:
                        if mode == "Online Mode" and api_key and steamid:
                            schema = get_achievement_schema(api_key, app_id)
                            player_achievements = get_player_achievements(api_key, steamid, app_id)
                        elif mode == "Offline Mode":
                            # Load cached schema and player achievements if available
                            schema = None
                            player_achievements = None
                            achievements_schema_file = os.path.join("cache/game_details", f"game_{app_id}_achievements.pkl")
                            player_achievements_file = os.path.join("cache/game_details", f"game_{app_id}_player_achievements.pkl")
                            if os.path.exists(achievements_schema_file):
                                with open(achievements_schema_file, 'rb') as f:
                                    schema = pickle.load(f)
                            if os.path.exists(player_achievements_file):
                                with open(player_achievements_file, 'rb') as f:
                                    player_achievements = pickle.load(f)
                        else:
                            schema = None
                            player_achievements = None
                        if schema and player_achievements:
                            total_achievements = len(schema)
                            completed_achievements = sum(1 for a in player_achievements if a.get("achieved") == 1)
                            percent = (completed_achievements / total_achievements) * 100 if total_achievements > 0 else 0
                            st.write(f"**Achievements:** {completed_achievements} / {total_achievements} ({percent:.0f}%)")
                            st.progress(percent / 100)
                    
                    # Short description
                    if 'short_description' in game_details:
                        description = game_details['short_description']
                        st.write("**Description:**")
                        st.write(description)
                    
                    # Steam user rating
                    if 'recommendations' in game_details:
                        total_recommendations = game_details['recommendations'].get('total', 0)
                        if total_recommendations > 0:
                            st.write(f"**Total Steam Reviews:** {total_recommendations:,}")
                            st.write("💡 *Note: Steam rating (Very Positive, etc.) requires additional API access*")
                    
                    # User score (if available)
                    if 'metacritic' in game_details and game_details['metacritic'].get('url'):
                        st.write(f"**User Score:** [View on Metacritic]({game_details['metacritic']['url']})")
                    
                    # PC Requirements
                    if 'pc_requirements' in game_details and game_details['pc_requirements']:
                        with st.expander("💻 PC Requirements"):
                            if isinstance(game_details['pc_requirements'], dict):
                                if 'minimum' in game_details['pc_requirements']:
                                    st.write("**Minimum:**")
                                    clean_min = clean_html_text(game_details['pc_requirements']['minimum'])
                                    st.text(clean_min)
                                if 'recommended' in game_details['pc_requirements']:
                                    st.write("**Recommended:**")
                                    clean_rec = clean_html_text(game_details['pc_requirements']['recommended'])
                                    st.text(clean_rec)
                            else:
                                clean_req = clean_html_text(game_details['pc_requirements'])
                                st.text(clean_req)
                    
                    # DRM Notice
                    if 'drm_notice' in game_details and game_details['drm_notice']:
                        st.write(f"**DRM:** {game_details['drm_notice']}")
                    
                    # Age Rating
                    if 'required_age' in game_details:
                        try:
                            age = int(game_details['required_age'])
                            if age > 0:
                                st.write(f"**Age Rating:** {age}+")
                        except (ValueError, TypeError):
                            # If required_age is not a valid number, skip it
                            pass
                    
                    # Languages
                    if 'supported_languages' in game_details:
                        clean_languages = clean_html_text(game_details['supported_languages'])
                        st.write(f"**Languages:** {clean_languages}")
                    
                    # Categories (Single-player, Multi-player, etc.)
                    if 'categories' in game_details and game_details['categories']:
                        categories = [cat['description'] for cat in game_details['categories']]
                        st.write(f"**Categories:** {', '.join(categories)}")
                    
                    # Price Info
                    if 'price_overview' in game_details and game_details['price_overview']:
                        price_info = game_details['price_overview']
                        if price_info.get('final') == 0:
                            st.write("**Price:** Free")
                        else:
                            final_price = price_info.get('final_formatted', 'N/A')
                            original_price = price_info.get('initial_formatted', 'N/A')
                            if final_price != original_price:
                                st.write(f"**Price:** ~~{original_price}~~ **{final_price}** (on sale!)")
                            else:
                                st.write(f"**Price:** {final_price}")
                    
                    # Developer & Publisher
                    if 'developers' in game_details and game_details['developers']:
                        st.write(f"**Developer:** {', '.join(game_details['developers'])}")
                    if 'publishers' in game_details and game_details['publishers']:
                        st.write(f"**Publisher:** {', '.join(game_details['publishers'])}")
                    
                    # Platform Support
                    platforms = []
                    if game_details.get('platforms', {}).get('windows', False):
                        platforms.append("Windows")
                    if game_details.get('platforms', {}).get('mac', False):
                        platforms.append("Mac")
                    if game_details.get('platforms', {}).get('linux', False):
                        platforms.append("Linux")
                    if platforms:
                        st.write(f"**Platforms:** {', '.join(platforms)}")
                    
                    # Controller Support
                    if 'controller_support' in game_details and game_details['controller_support']:
                        st.write(f"**Controller:** {game_details['controller_support']}")
                    
                    # Cloud Saves
                    if 'categories' in game_details and game_details['categories']:
                        cloud_save = any('Cloud Saves' in cat.get('description', '') for cat in game_details['categories'])
                        if cloud_save:
                            st.write("**Cloud Saves:** ✅ Supported")
                    
                    # Family Sharing
                    if 'categories' in game_details and game_details['categories']:
                        family_sharing = any('Family Sharing' in cat.get('description', '') for cat in game_details['categories'])
                        if family_sharing:
                            st.write("**Family Sharing:** ✅ Supported")
                    
                    # Remote Play
                    if 'categories' in game_details and game_details['categories']:
                        remote_play = any('Remote Play' in cat.get('description', '') for cat in game_details['categories'])
                        if remote_play:
                            st.write("**Remote Play:** ✅ Supported")
                
                # Steam store link
                if app_id:
                    st.markdown(f"[View on Steam Store](https://store.steampowered.com/app/{app_id})")
                
                # Store game details in session state for sidebar
                if game_details:
                    st.session_state.selected_game = game_details

    else:
        if exclude_rolled and st.session_state.rolled_games:
            st.warning(f"No more games available with less than {max_hours} hours of playtime. You've rolled all available games!")
            if st.button("🔄 Reset Rolled Games"):
                st.session_state.rolled_games.clear()
                st.rerun()
        else:
            st.warning(f"No games found with less than {max_hours} hours of playtime. Try increasing the playtime limit!") 