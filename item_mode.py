from pathlib import Path
from pico2d import *

import game_framework
import game_world
import play_mode


image = None
font = None


def init():
    global image, font
    image = load_image(str(Path(__file__).resolve().parent / 'item_select.png'))
    font = load_font('C:/Windows/Fonts/malgun.ttf', 20)


def finish():
    global image, font
    image = None
    font = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            if not getattr(event, 'repeat', 0):
                game_framework.pop_mode()
                return
        elif event.type == SDL_KEYDOWN:
            choices = {SDLK_0: 0, SDLK_1: 1, SDLK_2: 2}
            if event.key in choices and not getattr(event, 'repeat', 0):
                play_mode.boy.select_item(choices[event.key])
        elif event.type == SDL_KEYUP:
            # Track movement releases while the explanation is open.
            play_mode.boy.handle_event(event)


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    image.draw(get_canvas_width() / 2, get_canvas_height() / 2)
    x = get_canvas_width() / 2 - 200
    y = get_canvas_height() / 2 - 155
    font.draw(x, y, 'I를 누르면 설명창이 열립니다.', (0, 0, 0))
    font.draw(x, y - 30, 'I를 한 번 더 누르면 설명창이 닫힙니다.', (0, 0, 0))
    update_canvas()
