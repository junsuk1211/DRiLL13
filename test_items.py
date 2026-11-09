"""Headless integration checks: python -m unittest -v test_items."""
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pico2d
import game_framework
import game_world
import boy
import ball
import grass
import play_mode
import item_mode
import pause_mode


class ItemModeTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.patches = []
        def mock(module, name, value):
            patcher = patch.object(module, name, value)
            patcher.start()
            self.patches.append(patcher)
        def image(path):
            self.assertTrue(Path(path).is_file())
            return SimpleNamespace(draw=lambda *a: None, clip_draw=lambda *a: None)
        for module in (boy, play_mode):
            mock(module, 'get_time', lambda: self.now)
        for module in (boy, ball, grass, item_mode):
            mock(module, 'load_image', image)
        for module in (boy, ball):
            mock(module, 'get_canvas_width', lambda: 800)
        game_world.clear()
        ball.Ball.images.clear()
        game_framework.stack = [play_mode]
        game_framework.running = True
        play_mode.init()

    def tearDown(self):
        while game_framework.stack:
            game_framework.stack.pop().finish()
        game_framework.running = False
        for patcher in reversed(self.patches):
            patcher.stop()

    def key(self, module, key, kind=pico2d.SDL_KEYDOWN, repeat=0):
        event = SimpleNamespace(type=kind, key=key, repeat=repeat)
        with patch.object(module, 'get_events', return_value=[event]):
            module.handle_events()

    def balls(self):
        return [o for layer in game_world.world for o in layer if isinstance(o, ball.Ball)]

    def test_default_space_fires_normal_ball_without_automatic_fire(self):
        self.assertIsNone(play_mode.boy.selected_item)
        self.now = 1.0
        play_mode.update()
        self.assertEqual(self.balls(), [])
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(len(self.balls()), 1)
        self.assertEqual(self.balls()[0].size, 21)
        self.assertEqual(self.balls()[0].velocity, 10)
        self.now += 1.0
        play_mode.update()
        self.assertEqual(len(self.balls()), 1)
        self.key(play_mode, pico2d.SDLK_LEFT)
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(len(self.balls()), 2)
        self.assertEqual(self.balls()[-1].velocity, -10)

    def test_option_zero_disables_manual_fire_from_default(self):
        self.key(play_mode, pico2d.SDLK_i)
        self.key(item_mode, pico2d.SDLK_0)
        self.key(item_mode, pico2d.SDLK_i)
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.now = 1.0
        play_mode.update()
        self.assertEqual(self.balls(), [])

    def test_selected_size_only_fires_on_space(self):
        for selection, size in ((1, 21), (2, 41)):
            self.key(play_mode, pico2d.SDLK_i)
            self.key(item_mode, getattr(pico2d, f'SDLK_{selection}'))
            self.key(item_mode, pico2d.SDLK_i)
            count = len(self.balls())
            self.now += 0.49
            play_mode.update()
            self.assertEqual(len(self.balls()), count)
            self.now += 0.02
            play_mode.update()
            self.assertEqual(len(self.balls()), count)
            self.key(play_mode, pico2d.SDLK_SPACE)
            self.assertEqual(len(self.balls()), count + 1)
            self.assertEqual(self.balls()[-1].size, size)
        self.key(play_mode, pico2d.SDLK_i)
        self.key(item_mode, pico2d.SDLK_0)
        self.key(item_mode, pico2d.SDLK_i)
        count = len(self.balls())
        self.now += 10
        play_mode.update()
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(len(self.balls()), count)

    def test_menu_freezes_world_and_preserves_objects(self):
        player = play_mode.boy
        player.select_item(1)
        player.fire_ball()
        player.handle_event(SimpleNamespace(type=pico2d.SDL_KEYDOWN, key=pico2d.SDLK_RIGHT))
        positions = (player.x, player.frame, self.balls()[0].x)
        self.key(play_mode, pico2d.SDLK_i)
        self.now = 20
        item_mode.update()
        self.assertEqual(positions, (player.x, player.frame, self.balls()[0].x))
        self.key(item_mode, pico2d.SDLK_i, repeat=1)
        self.assertIs(game_framework.stack[-1], item_mode)
        self.key(item_mode, pico2d.SDLK_RIGHT, kind=pico2d.SDL_KEYUP)
        self.key(item_mode, pico2d.SDLK_i)
        self.assertIs(play_mode.boy, player)
        self.assertEqual(player.dir, 0)
        self.assertIsNone(item_mode.image)
        play_mode.update()
        self.assertEqual(len(self.balls()), 1)
        self.now += 0.51
        play_mode.update()
        self.assertEqual(len(self.balls()), 1)
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(len(self.balls()), 2)

    def test_selection_during_menu_waits_for_space_after_resume(self):
        self.key(play_mode, pico2d.SDLK_i)
        self.now = 5
        self.key(item_mode, pico2d.SDLK_2)
        self.now = 15
        self.key(item_mode, pico2d.SDLK_i)
        play_mode.update()
        self.assertEqual(self.balls(), [])
        self.now += 0.51
        play_mode.update()
        self.assertEqual(self.balls(), [])
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(self.balls()[0].size, 41)

    def test_pause_resume_does_not_fire_selected_ball(self):
        play_mode.boy.select_item(1)
        self.key(play_mode, pico2d.SDLK_p)
        self.now = 30
        pause_mode.update()
        self.assertEqual(self.balls(), [])
        self.key(pause_mode, pico2d.SDLK_p)
        play_mode.update()
        self.assertEqual(self.balls(), [])
        self.now += 0.51
        play_mode.update()
        self.assertEqual(self.balls(), [])
        self.key(play_mode, pico2d.SDLK_SPACE)
        self.assertEqual(len(self.balls()), 1)

    def test_quit_from_item_mode_and_new_game_reset(self):
        play_mode.boy.select_item(2)
        self.key(play_mode, pico2d.SDLK_i)
        self.key(item_mode, None, kind=pico2d.SDL_QUIT)
        self.assertFalse(game_framework.running)
        game_framework.pop_mode()
        play_mode.finish()
        play_mode.init()
        self.assertIsNone(play_mode.boy.selected_item)
        self.assertEqual(self.balls(), [])


if __name__ == '__main__':
    unittest.main()
