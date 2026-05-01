import streamlit as st
import os
from openai import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# --- Clients ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=st.secrets["SPOTIPY_CLIENT_ID"],
    client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
    redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
    scope="playlist-modify-public"
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
