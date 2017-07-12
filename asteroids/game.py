import random
import thread
import time
from Tkinter import *
from tkFont import Font
from asteroids import audio, util

class Display(object):

    def __init__(self):
        self.root = Tk(sync=True)
        self._width = 0
        self._height = 0
        self._caption = ''

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, (width, height)):
        self._width = width
        self._height = height

        self.root.geometry('%dx%d' % (width, height))

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, caption):
        self._caption = caption

        self.root.title(caption)

    def update(self):
        self.root.update()

class Game(object):

    def __init__(self, scene, width=1280, height=720, caption='Asteroids'):
        self.display = Display()
        self.display.size = (width, height)
        self.display.caption = caption

        self.audio_manager = audio.AudioManager()

        self._last_scene = None
        self._current_scene = scene(self, self.display)

        self.shutdown = False

    @property
    def current_scene(self):
        return self._current_scene

    @current_scene.setter
    def current_scene(self, scene):
        if self._current_scene:
            self._current_scene.destroy()
            self._last_scene = self._current_scene

        self._current_scene = scene(self, self.display)
        self._current_scene.setup()

    def setup(self):
        self.current_scene.setup()

    def update(self):
        if self.current_scene.active:
            self.current_scene.update()

    def destroy(self):
        self.current_scene.destroy()

    def execute(self):
        self.update()
        self.display.update()

    def mainloop(self):
        while not self.shutdown:
            try:
                self.execute()
            except (KeyboardInterrupt, SystemExit):
                break

        self.destroy()

class Scene(object):

    def __init__(self, root, master):
        self.root = root
        self.master = master
        self.active = True

    def setup(self):
        self.canvas = Frame(self.master.root, width=self.master.width, height=self.master.height,
            background='black', highlightthickness=0)

        self.canvas.focus_set()
        self.canvas.pack()

    def update(self):
        if hasattr(self, 'canvas'):
            if self.canvas['width'] != self.master.root.winfo_width() or self.canvas['height'] != self.master.root.winfo_height():
                self.canvas['width'], self.canvas['height'] = self.master.root.winfo_width(), self.master.root.winfo_height()

    def destroy(self):
        self.canvas.destroy()
        self.active = False

class MainMenu(Scene):

    def setup(self):
        super(MainMenu, self).setup()

        self.music = self.root.audio_manager.load('assets/audio/music/main_menu.wav')
        self.music.play(True)

        self.button_down = self.root.audio_manager.load('assets/audio/sfx/button_down.wav')
        self.button_over = self.root.audio_manager.load('assets/audio/sfx/button_over.wav')

        image = util.load_image_photo('assets/menu/logo.png')
        self.logo = Label(self.canvas, image=image,
            background='black')

        self.logo.image = image
        self.logo.pack()

        # load the desired font into memory
        util.load_font('assets/font/Pixeled.ttf')

        # now create a new font object using the font loaded in memory
        text_font = Font(family='Pixeled', size=40)

        self.play_button = Label(self.canvas, text='Play', font=text_font,
            background='black', foreground='white')

        self.play_button.pack()
        self.play_button.bind('<Enter>', self.handle_mouse_enter_play)
        self.play_button.bind('<Leave>', self.handle_mouse_exit_play)
        self.play_button.bind('<Button-1>', self.handle_play)

        self.quit_button = Label(self.canvas, text='Quit', font=text_font,
            background='black', foreground='white')

        self.quit_button.pack()
        self.quit_button.bind('<Enter>', self.handle_mouse_enter_quit)
        self.quit_button.bind('<Leave>', self.handle_mouse_exit_quit)
        self.quit_button.bind('<Button-1>', self.handle_quit)

    def handle_mouse_enter_play(self, event):
        self.root.audio_manager.beep()
        self.play_button['foreground'] = 'red'

    def handle_mouse_exit_play(self, event):
        self.play_button['foreground'] = 'white'

    def handle_play(self, event):
        self.root.audio_manager.beep()
        self.root.current_scene = GameLevel

    def handle_mouse_enter_quit(self, event):
        self.root.audio_manager.beep()
        self.quit_button['foreground'] = 'red'

    def handle_mouse_exit_quit(self, event):
        self.quit_button['foreground'] = 'white'

    def handle_quit(self, event):
        self.root.audio_manager.beep()
        self.root.shutdown = True

    def update(self):
        super(MainMenu, self).update()

        self.logo.place(x=self.master.root.winfo_width() / 2, y=self.master.root.winfo_height() / 4, anchor='center')
        self.play_button.place(x=self.master.root.winfo_width() / 2, y=self.master.root.winfo_height() / 2, anchor='center')
        self.quit_button.place(x=self.master.root.winfo_width() / 2, y=self.master.root.winfo_height() / 2 + self.logo.image.height(), anchor='center')

    def destroy(self):
        super(MainMenu, self).destroy()

        self.music.stop()
        self.root.audio_manager.unload(self.music)

        self.logo.destroy()
        self.play_button.destroy()
        self.quit_button.destroy()

class GameLevel(Scene):

    def setup(self):
        super(GameLevel, self).setup()

        self.music = self.root.audio_manager.load('assets/audio/music/level.wav')
        self.music.play(True)

        self.ending_music = self.root.audio_manager.load('assets/audio/music/ending')

        background = util.load_image_photo('assets/stars.png')
        self.background = Label(self.canvas, image=background, background='black')
        self.background.image = background
        self.background.pack()

        ship = util.load_image_photo('assets/player.png')
        self.ship = Label(self.canvas, image=ship, background='black')
        self.ship.image = ship
        self.ship.x = self.master.root.winfo_width() / 2
        self.ship.y = self.master.root.winfo_height() - ship.height()
        self.ship.pack()

        self.ship_speed = 25
        self.ship_missile_speed = 30
        self.ship_missiles = []
        self.num_missiles = 25

        self.asteroid_speed = 40
        self.asteroids = []
        self.num_asteroids = 15

        text_font = Font(family='Pixeled', size=15)
        self.current_score = 0

        self.score = Label(self.canvas, text='', font=text_font,
            background='black', foreground='white')

        self.score.x = 80
        self.score.y = 20
        self.score.pack()

        self.end_game = None

        self.moving_forward = False
        self.moving_backward = False
        self.moving_right = False
        self.moving_left = False
        self.firing = False
        self.paused = False

        self.canvas.bind('<Up>', self.handle_move_forward)
        self.canvas.bind('<KeyRelease-Up>', self.handle_move_forward_release)

        self.canvas.bind('<Down>', self.handle_move_backward)
        self.canvas.bind('<KeyRelease-Down>', self.handle_move_backward_release)

        self.canvas.bind('<Right>', self.handle_move_right)
        self.canvas.bind('<KeyRelease-Right>', self.handle_move_right_release)

        self.canvas.bind('<Left>', self.handle_move_left)
        self.canvas.bind('<KeyRelease-Left>', self.handle_move_left_release)

        self.canvas.bind('<space>', self.handle_fire)
        self.canvas.bind('<KeyRelease-space>', self.handle_fire_release)

        self.canvas.bind('<Return>', self.handle_pause)

        self.current_time = 0
        self.timer_active = True

        self.time = Label(self.canvas, text='', font=text_font,
            background='black', foreground='white')

        self.time.x = self.master.root.winfo_width() - 80
        self.time.y = 20
        self.time.pack()

        thread.start_new_thread(self.update_time, ())

    def update_time(self):
        while self.timer_active:
            if self.paused:
                continue

            self.current_time += 1
            time.sleep(1)

    def update(self):
        if self.paused:
            return

        super(GameLevel, self).update()

        if self.ship:
            self.ship.place(x=self.ship.x, y=self.ship.y, anchor='center')

        if self.score:
            self.score.place(x=self.score.x, y=self.score.y, anchor='center')
            self.score['text'] = 'Score: %d' % self.current_score

        if self.time:
            self.time.place(x=self.time.x, y=self.time.y, anchor='center')
            self.time['text'] = 'Time: %d' % self.current_time

        if self.end_game:
            self.end_game.place(x=self.end_game.x, y=self.end_game.y, anchor='center')

        self.update_key()

        for missile in self.ship_missiles:
            if not self.ship:
                return

            if missile.y <= 0:
                missile.destroy()
                self.ship_missiles.remove(missile)
                continue

            missile.y -= self.ship_missile_speed
            missile.place(x=missile.x, y=missile.y)

        for asteroid in self.asteroids:
            if not self.ship:
                return

            if asteroid.y >= self.master.root.winfo_height():
                asteroid.destroy()
                self.asteroids.remove(asteroid)
                continue

            # missile collision detection
            for missile in self.ship_missiles:
                if missile.x >= asteroid.x and missile.x <= asteroid.x + asteroid.image.width() and missile.y >= asteroid.y - asteroid.image.height() and missile.y <= asteroid.y:
                    asteroid.destroy()
                    self.asteroids.remove(asteroid)

                    missile.destroy()
                    self.ship_missiles.remove(missile)

                    self.current_score += 1
                    return

            # player collision detection
            if self.ship.x >= asteroid.x and self.ship.x <= asteroid.x + asteroid.image.width() and self.ship.y >= asteroid.y - asteroid.image.height() and self.ship.y <= asteroid.y:
                self.end()
                return

            asteroid.y += asteroid.speed
            asteroid.place(x=asteroid.x, y=asteroid.y)

        if len(self.asteroids) < self.num_asteroids:
            self.handle_asteroid()

    def update_key(self):
        if not self.ship:
            return

        if self.moving_forward and not self.ship.y - self.ship.image.height() / 2 <= 0:
            self.ship.y -= self.ship_speed
        elif self.moving_backward and not self.ship.y + self.ship.image.height() / 2 >= self.master.root.winfo_height():
            self.ship.y += self.ship_speed

        if self.moving_right and not self.ship.x + self.ship.image.width() / 2 >= self.master.root.winfo_width():
            self.ship.x += self.ship_speed
        elif self.moving_left and not self.ship.x - self.ship.image.width() / 2 <= 0:
            self.ship.x -= self.ship_speed

        if self.firing and len(self.ship_missiles) < self.num_missiles:
            self.handle_do_fire()

    def handle_move_forward(self, event):
        self.moving_forward = True

    def handle_move_forward_release(self, event):
        self.moving_forward = False

    def handle_move_backward(self, event):
        self.moving_backward = True

    def handle_move_backward_release(self, event):
        self.moving_backward = False

    def handle_move_right(self, event):
        self.moving_right = True

    def handle_move_right_release(self, event):
        self.moving_right = False

    def handle_move_left(self, event):
        self.moving_left = True

    def handle_move_left_release(self, event):
        self.moving_left = False

    def handle_fire(self, event):
        self.firing = True

    def handle_fire_release(self, event):
        self.firing = False

    def handle_do_fire(self):
        self.root.audio_manager.beep()

        image = util.load_image_photo('assets/missle.png')

        # first gun
        missile = Label(self.canvas, image=image, background='black')
        self.ship_missiles.append(missile)

        missile.image = image
        missile.x = self.ship.x - self.ship.image.width() / 2
        missile.y = self.ship.y - self.ship.image.height() / 2
        missile.pack()

        # second gun
        missile = Label(self.canvas, image=image, background='black')
        self.ship_missiles.append(missile)

        missile.image = image
        missile.x = self.ship.x + self.ship.image.width() / 2
        missile.y = self.ship.y - self.ship.image.height() / 2
        missile.pack()

    def handle_pause(self, event):
        if not self.paused:
            self.paused = True
        else:
            self.paused = False

    def handle_asteroid(self):
        images = [
            'assets/asteroids/asteroid-small.png',
            'assets/asteroids/asteroid-big.png'
        ]

        image = util.load_image_photo(random.choice(images))
        asteroid = Label(self.canvas, image=image, background='black')
        self.asteroids.append(asteroid)

        asteroid.image = image
        asteroid.x = random.randrange(0, self.master.root.winfo_width())
        asteroid.y = 0
        asteroid.speed = random.random() * self.asteroid_speed
        asteroid.pack()

    def end(self):
        if self.music.playing:
            self.music.stop()

        self.ending_music.play(True)

        self.ship.destroy()
        self.ship = None

        for missile in self.ship_missiles:
            missile.destroy()
            self.ship_missiles.remove(missile)

        for asteroid in self.asteroids:
            asteroid.destroy()
            self.asteroids.remove(asteroid)

        self.score.destroy()
        self.score = None

        self.timer_active = False
        self.time.destroy()
        self.time = None

        text_font = Font(family='Pixeled', size=40)
        self.end_game = Label(self.canvas, text='Game Over...', font=text_font,
            background='black', foreground='white')

        self.end_game.x = self.master.root.winfo_width() / 2
        self.end_game.y = self.master.root.winfo_height() / 2
        self.end_game.pack()

        self.canvas.bind('<Escape>', self.handle_back)

    def handle_back(self, event):
        if self.ending_music.playing:
            self.ending_music.stop()

        super(GameLevel, self).destroy()
        self.root.current_scene = GameLevel
