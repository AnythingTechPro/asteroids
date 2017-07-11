import winsound
import thread

class Audio(object):

    def __init__(self, audio_manager, filename):
        self.audio_manager = audio_manager
        self.filename = filename
        self.playing = False

    def play(self, loop=False, no_stop=True):
        if self.playing:
            return

        thread.start_new_thread(self.do_play, (loop, no_stop,))

    def do_play(self, loop, no_stop):
        flags = winsound.SND_FILENAME | winsound.SND_ASYNC

        if loop:
            flags |= winsound.SND_LOOP

        if no_stop:
            flags |= winsound.SND_NOSTOP

        winsound.PlaySound(self.filename, flags)
        self.playing = True

    def stop(self):
        if not self.playing:
            return

        thread.start_new_thread(self.do_stop, ())

    def do_stop(self):
        winsound.PlaySound(self.filename, winsound.SND_PURGE)
        self.playing = False

class AudioManager(object):

    def __init__(self):
        self.audio = []

    def has_audio(self, audio):
        return audio in self.audio

    def add_audio(self, audio):
        if self.has_audio(audio):
            return

        self.audio.append(audio)

    def remove_audio(self, audio):
        if not self.has_audio(audio):
            return

        audio.stop()
        self.audio.remove(audio)

    def load(self, filename):
        audio = Audio(self, filename)
        self.add_audio(audio)

        return audio

    def unload(self, audio):
        self.remove_audio(audio)

    def beep(self):
        return winsound.MessageBeep()
