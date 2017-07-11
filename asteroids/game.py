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

        background = util.load_image_photo('assets/stars.png')
        self.background = Label(self.canvas, image=background, background='black')
        self.background.image = background
        self.background.pack()

        ship = util.load_image_photo('assets/player.png')
        self.ship = Label(self.canvas, image=ship, background='black')
        self.ship.image = ship
        self.ship.pack()

        self.ship_x = self.master.root.winfo_width() / 2
        self.ship_y = self.master.root.winfo_height() - ship.height()
        self.ship_speed = 25

        self.canvas.bind('<Right>', self.handle_move_right)
        self.canvas.bind('<Left>', self.handle_move_left)

    def update(self):
        super(GameLevel, self).update()

        self.ship.place(x=self.ship_x, y=self.ship_y, anchor='center')

    def handle_move_right(self, event):
        if self.ship_x + self.ship.image.width() / 2 >= self.master.root.winfo_width():
            return

        self.ship_x += self.ship_speed

    def handle_move_left(self, event):
        if self.ship_x - self.ship.image.width() / 2 <= 0:
            return

        self.ship_x -= self.ship_speed
