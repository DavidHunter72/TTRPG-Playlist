import streamlit as st
import os
from openai import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #000000);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

/* Smooth animation */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Optional: make text easier to read */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.4);
    z-index: -1;
}
</style>
""", unsafe_allow_html=True)
# --- Clients ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=st.secrets["SPOTIPY_CLIENT_ID"],
    client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"]
))

# --- Generate playlist ---
def generate_playlist(theme):
    prompt = f"""
    You are a game master.

    Create exactly 6 songs for a TTRPG session based on:
    {theme}

    Format:
    Song - Artist
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    songs = [line for line in text.split("\n") if "-" in line]
    return songs[:6]

# --- Spotify search ---
def search_spotify(song):
    result = sp.search(q=song, type="track", limit=1)
    if result["tracks"]["items"]:
        track = result["tracks"]["items"][0]
        return {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "url": track["external_urls"]["spotify"],
            "image": track["album"]["images"][0]["url"]
        }
    return None

# --- UI ---
st.title("🎲 TTRPG Playlist Generator")

theme = st.text_input("Describe your scene:")

if st.button("Generate"):
    if theme:
        with st.spinner("Generating..."):
            songs = generate_playlist(theme)

        for s in songs:
            track = search_spotify(s)
            if track:
                st.image(track["image"], width=100)
                st.markdown(f"[{track['name']} - {track['artist']}]({track['url']})")
            else:
                st.write(f"Not found: {s}")
