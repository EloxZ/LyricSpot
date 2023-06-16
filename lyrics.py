import requests
import asyncio
import threading


class Lyrics:
    # Current song data
    current_song_string = ""
    current_lyrics = ""
    lyrics_available = False
    song_changed = False
    thread = None

    # Prevent instantiation
    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    @staticmethod
    def start_lyrics_thread(user_spotify, current_msg, current_lyric, scale):
        # Creating async task
        loop = asyncio.new_event_loop()
        loop.create_task(Lyrics.now_playing(user_spotify, current_msg, current_lyric, scale))

        # Creating coroutine of now_playing()
        Lyrics.thread = threading.Thread(name='background', target=loop.run_forever)
        Lyrics.thread.daemon = True
        Lyrics.thread.start()

    # Get song string
    @staticmethod
    def song_string(song):
        return song.item.artists[0].name + " " + song.item.name

    # Format song data in a string pattern
    @staticmethod
    def song_to_msg(song, lyrics=False, delay=200):
        if song.is_playing:
            msg = "[Playing ▶] "
        else:
            msg = "[Paused II] "

        msg += Lyrics.millis_to_timestamp_string(song.progress_ms)
        msg += " ♪ " + song.item.name + " 【"

        artists_string = ""
        for artist in song.item.artists:
            artists_string += artist.name + ", "

        msg += artists_string[:-2] + "】"
        if lyrics:
            lyric = Lyrics.get_current_lyric(Lyrics.song_string(song), song.item.id, song.progress_ms, delay)
            if not Lyrics.lyrics_available:
                lyric = "¯\_(ツ)_/¯"

        else:
            lyric = ""

        return msg, lyric

    # Format song data in a string pattern
    @staticmethod
    def get_current_lyric(song_string, song_id, ms, delay):
        lyric = ""
        try:
            if song_string != Lyrics.current_song_string:
                Lyrics.song_changed = True
                Lyrics.current_song_string = song_string
                query = "https://spotify-lyric-api.herokuapp.com/?trackid=" + song_id
                response = requests.get(query)

                Lyrics.lyrics_available = False
                if response.status_code == 200:
                    Lyrics.current_lyrics = response.json()
                    if not Lyrics.current_lyrics['error'] and Lyrics.current_lyrics['syncType'] == "LINE_SYNCED":
                        Lyrics.lyrics_available = True

            if Lyrics.lyrics_available:
                for entry in Lyrics.current_lyrics["lines"]:
                    if int(entry['startTimeMs']) <= ms + delay:
                        lyric = entry['words']
                    else:
                        break
        except Exception as e:
            print(str(e))

        return lyric

    # Async function retrieving data
    @staticmethod
    async def now_playing(user_spotify, current_msg, current_lyric, scale):
        while True:
            try:
                delay = 200
                if scale:
                    delay = int(scale.get())
                song = await user_spotify.playback_currently_playing()
                if song and song.item:
                    msg, lyric = Lyrics.song_to_msg(song, lyrics=True, delay=delay)
                    current_msg.set(msg)
                    if lyric != "" or Lyrics.song_changed:
                        Lyrics.song_changed = False
                        current_lyric.set(lyric)
            except ValueError as e:
                print(str(e))

            await asyncio.sleep(0.8)

    # Convert millis to hours, mins, secs
    @staticmethod
    def convert_millis(millis):
        seconds = (millis / 1000) % 60
        minutes = (millis / (1000 * 60)) % 60
        hours = (millis / (1000 * 60 * 60)) % 24
        return int(hours), int(minutes), int(seconds)

    # Convert millis to timestamp string
    @staticmethod
    def millis_to_timestamp_string(millis):
        hours, minutes, seconds = Lyrics.convert_millis(millis)
        string = "["
        if hours > 0:
            string += str(hours) + ":"
        string += str(minutes) + ":"
        if seconds < 10:
            string += "0"
        string += str(seconds) + "]"

        return string
