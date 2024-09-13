import webbrowser
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pygame
import os
import openai
import requests
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth


recognizer = sr.Recognizer()
engine = pyttsx3.init()
# can be generated from https://newsapi.org/
newsapi = "your api key" 

# Text-to-speech function (pyttsx3)
def speak_default(text):
    engine.say(text)
    engine.runAndWait()
# google text to speech(we can use either gtts or pyttsx3)
def speak(text): 
    tts = gTTS(text)
    tts.save('temp.mp3')
    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove('temp.mp3')

# Spotify credentials can be generated on https://developer.spotify.com/  and as we are locally using spotify on browser the redirect_url can be the same.
CLIENT_ID = 'Your_Client_id' 
CLIENT_SECRET = 'Your_Secret_id'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

def play_song(song_name):
    speak(f"Searching for {song_name} on Spotify.")
    
    # Search for the song on Spotify
    result = sp.search(q=song_name, type='track', limit=1)
    if result['tracks']['items']:
        song = result['tracks']['items'][0]
        song_uri = song['uri']
        song_title = song['name']
        artist_name = song['artists'][0]['name']

        # Play the song on Spotify
        sp.start_playback(uris=[song_uri])

        # Make the assistant speak the output
        speak(f"Playing {song_title} by {artist_name}. Enjoy!")  
    else:
        # If song not found
        speak(f"Sorry, I couldn't find {song_name} on Spotify.")
        
def aiapi(command): # openai api key for general responses can be generated on https://platform.openai.com/
    try:
        openai.api_key = "apikey"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Assistme. Give short responses please"},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, I couldn't connect to AI services."    

def processcommand(c):

    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
    
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com")
        speak("Opening Facebook.")
    
    elif "open instagram" in c.lower():
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram.")
    
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    
    elif "news" in c.lower():
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles')
                for article in articles[:8]:
                    speak(article['title'])
            else:
                speak("Unable to fetch news at the moment.")
        except Exception as e:
            print(f"Error fetching news: {e}")
            speak("There was an error fetching the news.") 

    elif "play" in c.lower():
        song_name = command.lower().replace('play', '').strip()
        play_song(song_name)

    elif "day" in c.lower():
        today= datetime.datetime.today()
        print(today.strftime("%A"))
        speak(f"Today's day is {print}")

    elif "time" in c.lower():
        time = datetime.datetime.today()
        current_time = time.strftime("%I:%M %p")
        print(current_time)
        speak(f"The time is {print}")

    elif "date" in c.lower():
        today = datetime.datetime.now().strftime("%B %d, %Y")
        print(today)
        speak(f"Today's date is {today}")

    elif "stop" in c.lower():
        speak("Bye, have a nice day!")
        return False 
    
    else:
        output = aiapi(c)  
        speak(output)

    return True

if __name__ == "__main__":
    speak("Hi, how can I help you?")
    print("Say hello to intialiaze Assistme")
    while True:
        r = sr.Recognizer()
        print("Recognizing..")
        try:
            with sr.Microphone() as source:
                print("Say something!")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=10, phrase_time_limit=15)

            say = r.recognize_google(audio)
            print(f"Recognized: {say}")

            if say.lower() == "hello":
                speak("Yes")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    print("Assistme is active")
                    audio = r.listen(source, timeout=10, phrase_time_limit=15)
                    command = r.recognize_google(audio)
                print(f"Command recognized: {command}")
                if not processcommand(command):
                    break
        except sr.UnknownValueError:
            print("sorry, can you speak clearly.")
            speak("can you speak clearly")
            continue
        except Exception as e:
            print("Error; {0}".format(e))         
