from asteroids.game import Game, MainMenu

if __name__ == '__main__':
    game = Game(MainMenu)
    game.setup()
    game.mainloop()
