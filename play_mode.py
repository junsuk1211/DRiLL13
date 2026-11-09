from pico2d import *
import game_framework
import game_world
import title_mode
from boy import Boy
from grass import Grass


def handle_events():

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                import pause_mode
                game_framework.push_mode(pause_mode)
                return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            if not getattr(event, 'repeat', 0):
                import item_mode
                game_framework.push_mode(item_mode)
                return
        else:
            boy.handle_event(event)



def init():
    global boy
    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()
def finish():
    game_world.clear()


def pause():
    global paused_at
    paused_at = get_time()


def resume():
    # Exclude paused time from the boy's idle-to-sleep timer.
    now = get_time()
    boy.idle_started_at += now - max(paused_at, boy.idle_started_at)
    boy.last_shot_at += now - max(paused_at, boy.last_shot_at)


