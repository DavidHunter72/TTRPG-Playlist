import streamlit as st
from openai import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# -------------------------------
# 🔐 API CLIENT SETUP
# -------------------------------

# OpenAI client (uses Streamlit secrets)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Spotify client (read-only search)
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=st.secrets["SPOTIPY_CLIENT_ID"],
    client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"]
))

# -------------------------------
# 🎨 DYNAMIC ANIMATED BACKGROUND
# -------------------------------

def set_dynamic_background(theme):
    if "battle" in theme.lower():
        colors = "#3a0d0d, #7a1f1f, #000000"
    elif "forest" in theme.lower():
        colors = "#0f3d2e, #1b5e20, #000000"
    elif "mystery" in theme.lower():
        colors = "#1a1a2e, #16213e, #000000"
    else:
        colors = "#0f2027, #203a43, #2c5364, #000000"

    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        height: 100%;
    }}

    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(-45deg, {colors});
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
    }}

    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Dark overlay */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.45);
        z-index: -1;
    }}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 🤖 AI PLAYLIST GENERATION
# -------------------------------

def generate_playlist(theme):
    """Uses OpenAI to generate 6 themed songs."""
    prompt = f"""
    You are a game master.

    Create exactly 6 songs for a TTRPG session based on:
    {theme}

    Format:
    Song - Artist
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content
        songs = [line for line in text.split("\n") if "-" in line]
        return songs[:6]

    except Exception as e:
        st.error(f"Error generating playlist: {e}")
        return []

# -------------------------------
# 🎧 SPOTIFY SEARCH
# -------------------------------

def search_spotify(song):
    """Finds a song on Spotify and returns metadata."""
    try:
        result = sp.search(q=song, type="track", limit=1)

        if result["tracks"]["items"]:
            track = result["tracks"]["items"][0]
            return {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "url": track["external_urls"]["spotify"],
                "image": track["album"]["images"][0]["url"]
            }
    except Exception as e:
        st.warning(f"Spotify error: {e}")

    return None

# -------------------------------
# 🖥️ UI
# -------------------------------

st.set_page_config(page_title="TTRPG Playlist Generator", page_icon="🎲")

st.title("🎲 TTRPG Playlist Generator")
st.caption("AI-generated soundtracks for immersive tabletop storytelling")

# User input
theme = st.text_input("Describe your scene (e.g., boss battle, forest exploration):")

# Apply animated background
if theme:
    set_dynamic_background(theme)

# Generate button
if st.button("🎵 Generate Playlist"):
    if not theme:
        st.warning("Please enter a theme first.")
    else:
        with st.spinner("Summoning your soundtrack..."):
            songs = generate_playlist(theme)

        if songs:
            st.subheader("🎧 Your Playlist")

            for s in songs:
                track = search_spotify(s)

                if track:
                    cols = st.columns([1, 4])

                    with cols[0]:
                        st.image(track["image"], width=80)

                    with cols[1]:
                        st.markdown(f"**[{track['name']} - {track['artist']}]({track['url']})**")

                else:
                    st.write(f"❌ Not found: {s}")

        else:
            st.error("Failed to generate playlist. Try a different theme.")

# -------------------------------
# 📌 FOOTER
# -------------------------------

st.markdown("---")
st.caption(
    "Built with Streamlit, OpenAI, and Spotify API | "
    "Playlist export available in local version via OAuth"
)
