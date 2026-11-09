from pico2d import *

import game_framework
import play_mode


def init():
    pass


def finish():
    pass


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                game_framework.pop_mode()
                return
        elif event.type == SDL_KEYUP:
            # Remember released movement keys so movement cannot get stuck.
            play_mode.boy.handle_event(event)


def update():
    pass


def render():
    play_mode.render()
