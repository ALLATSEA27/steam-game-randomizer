# 🚀 Deployment Guide

This guide will help you deploy the Steam Game Randomizer to Streamlit Cloud.

## Prerequisites

- A GitHub account
- A Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

## Step 1: Create GitHub Repository

1. **Go to GitHub** and click "New repository"
2. **Name your repository** (e.g., `steam-game-randomizer`)
3. **Make it public** (required for free Streamlit Cloud)
4. **Don't initialize** with README (we already have one)
5. **Click "Create repository"**

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)
```bash
# Initialize git in your project folder
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit: Steam Game Randomizer"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Option B: Using GitHub Web Interface
1. **Upload files** through GitHub's web interface
2. **Make sure to include:**
   - `cached_app.py` (main app file)
   - `requirements.txt` (dependencies)
   - `README.md` (documentation)
   - `.gitignore` (excludes cache files)
   - `.streamlit/config.toml` (Streamlit configuration)

## Step 3: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure your app:**
   - **Repository:** Select your GitHub repository
   - **Branch:** `main` (or `master`)
   - **Main file path:** `cached_app.py`
   - **App URL:** Choose a custom subdomain (optional)
5. **Click "Deploy!"**

## Step 4: Configure Environment (Optional)

If you want to set environment variables or secrets:

1. **Go to your app settings** in Streamlit Cloud
2. **Navigate to "Secrets"**
3. **Add any configuration** if needed

## Important Notes

### Cache Behavior
- **Local cache** won't work on Streamlit Cloud
- **Users will need to** fetch data each time they use the app
- **Consider this** when using the app - it will be slower than local version

### API Key Security
- **Don't hardcode** your Steam API key in the app
- **Users should** provide their own API keys
- **The app is designed** to work with user-provided credentials

### Performance
- **First load** will be slower as it fetches data from Steam
- **Subsequent rolls** will be faster within the same session
- **Session data** is lost when the app is closed

## Troubleshooting

### App won't deploy
- **Check requirements.txt** has all dependencies
- **Verify main file path** is correct (`cached_app.py`)
- **Ensure repository is public** (for free tier)

### App loads but doesn't work
- **Check Streamlit Cloud logs** for errors
- **Verify all files** were uploaded correctly
- **Test locally first** to ensure code works

### Performance issues
- **This is expected** - Streamlit Cloud is slower than local
- **Consider** using the local version for better performance
- **Cache limitations** are normal in cloud deployment

## Local vs Cloud

| Feature | Local | Streamlit Cloud |
|---------|-------|-----------------|
| Speed | Fast | Slower |
| Cache | Persistent | Session-only |
| Setup | One-time | Per session |
| Cost | Free | Free tier available |
| Sharing | Manual | Easy sharing |

## Next Steps

1. **Test your deployed app**
2. **Share the URL** with friends
3. **Consider** adding features like:
   - User authentication
   - Persistent user data
   - More game filters
   - Social features

---

**Happy Deploying! 🚀** 