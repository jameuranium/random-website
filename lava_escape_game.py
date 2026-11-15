import argparse
import json
import os
import random
import sys

import panda3d
from panda3d.core import loadPrcFileData

loadPrcFileData(
    "",
    f'plugin-path {os.path.dirname(os.path.abspath(panda3d.__file__)).replace(os.sep, "/")}',
)
loadPrcFileData("", "load-display pandagl")

from ursina import (
    Button,
    DirectionalLight,
    Entity,
    Sky,
    Text,
    Ursina,
    Vec3,
    application,
    camera,
    color,
    destroy,
    held_keys,
    time,
    window,
)


def rgb(red, green, blue):
    return color.rgb(red / 255, green / 255, blue / 255)


class LavaEscape:
    def __init__(self, challenge_mode=False):
        self.challenge_mode = challenge_mode
        self.entities = []
        self.elapsed = 0.0
        self.spawn_elapsed = 0.0
        self.game_over = False
        self.space_was_down = False
        self.jump_velocity = 0.0
        self.ground_height = 0.68
        self.score = 0
        self.result_file = None

        self.floor = Entity(
            model="cube",
            color=rgb(55, 62, 82),
            position=(0, -0.3, 4),
            scale=(12, 0.5, 34),
            collider="box",
        )
        self.lava = Entity(
            model="plane",
            color=rgb(235, 70, 25),
            position=(0, -1.3, 4),
            scale=(80, 1, 100),
        )
        self.player = Entity(
            model="cube",
            color=rgb(80, 190, 255),
            position=(0, self.ground_height, -4),
            scale=(0.85, 1.1, 0.85),
            collider="box",
        )
        self.score_text = Text(
            text="SURVIVED: 0",
            position=(-0.46, 0.45),
            scale=1.5,
            color=color.white,
        )
        self.help_text = Text(
            text="WASD / ARROWS: MOVE     SPACE: JUMP     ESC: QUIT",
            position=(-0.46, 0.4),
            scale=0.65,
            color=color.azure,
        )
        self.challenge_text = Text(
            text="CHALLENGE MODE",
            position=(0.2, 0.45),
            scale=1,
            color=color.orange,
            enabled=challenge_mode,
        )
        self.game_over_text = Text(
            text="",
            origin=(0, 0),
            scale=2,
            color=color.white,
            enabled=False,
        )

        self.reset_button = Button(
            text="PLAY AGAIN",
            color=rgb(45, 170, 105),
            scale=(0.22, 0.07),
            position=(0, -0.22),
            enabled=False,
        )
        self.reset_button.on_click = self.restart

        self.spawn_obstacle()

    def spawn_obstacle(self):
        gate = random.random() < 0.32
        speed = 8.0 + self.elapsed * 0.11
        if self.challenge_mode:
            speed *= 1.22

        if gate:
            gap_width = random.uniform(2.2, 3.2)
            gap_center = random.uniform(-3.2, 3.2)
            left_edge = -5.7
            right_edge = 5.7
            left_width = gap_center - gap_width / 2 - left_edge
            right_width = right_edge - (gap_center + gap_width / 2)

            for center, width in (
                (left_edge + left_width / 2, left_width),
                (gap_center + gap_width / 2 + right_width / 2, right_width),
            ):
                if width <= 0.2:
                    continue
                entity = Entity(
                    model="cube",
                    color=rgb(235, 110, 50),
                    position=(center, 0.92, 16),
                    scale=(width, 1.9, 0.65),
                )
                self.entities.append({
                    "entity": entity,
                    "kind": "wall",
                    "speed": speed,
                    "half_width": width / 2,
                })
        else:
            ball = Entity(
                model="sphere",
                color=rgb(255, random.randint(90, 150), 35),
                position=(random.uniform(-4.8, 4.8), 0.8, 16),
                scale=1.5,
                rotation=(random.randrange(360), random.randrange(360), 0),
            )
            self.entities.append({
                "entity": ball,
                "kind": "ball",
                "speed": speed,
                "half_width": 0.75,
            })

    def collides(self, obstacle):
        entity = obstacle["entity"]
        z_close = abs(entity.z - self.player.z) < (
            0.65 if obstacle["kind"] == "wall" else 1.05
        )
        x_close = abs(entity.x - self.player.x) < (
            obstacle["half_width"] + 0.42
        )
        if not (x_close and z_close):
            return False
        if obstacle["kind"] == "wall":
            return self.player.y - 0.55 < 1.85
        return self.player.y - 0.55 < 1.45

    def finish(self):
        if self.game_over:
            return
        self.game_over = True
        self.score = int(self.elapsed)
        self.game_over_text.text = f"GAME OVER\nSURVIVED: {self.score}"
        self.game_over_text.enabled = True
        self.reset_button.enabled = True
        self.help_text.text = "PRESS R OR CLICK PLAY AGAIN     ESC: EXIT"

    def restart(self):
        for obstacle in self.entities:
            destroy_entity = obstacle["entity"]
            destroy(destroy_entity)
        self.entities.clear()
        self.elapsed = 0.0
        self.spawn_elapsed = 0.0
        self.jump_velocity = 0.0
        self.game_over = False
        self.score = 0
        self.player.position = (0, self.ground_height, -4)
        self.game_over_text.enabled = False
        self.reset_button.enabled = False
        self.help_text.text = "WASD / ARROWS: MOVE     SPACE: JUMP     ESC: QUIT"
        self.spawn_obstacle()

    def save_result(self):
        """Write the score for the arcade to read (called on ESC and when the window closes)."""
        if not self.result_file:
            return
        with open(self.result_file, "w", encoding="utf-8") as result_file:
            json.dump({"score": int(self.score)}, result_file)

    def update(self):
        if self.game_over:
            return

        dt = time.dt
        self.elapsed += dt
        self.score = int(self.elapsed)
        self.score_text.text = f"SURVIVED: {self.score}"

        move_x = held_keys["d"] + held_keys["right arrow"] - held_keys["a"] - held_keys["left arrow"]
        move_z = held_keys["w"] + held_keys["up arrow"] - held_keys["s"] - held_keys["down arrow"]
        self.player.x = max(-5.1, min(5.1, self.player.x + move_x * 8 * dt))
        self.player.z = max(-6.3, min(7.5, self.player.z + move_z * 7 * dt))

        space_down = held_keys["space"]
        if space_down and not self.space_was_down and self.player.y <= self.ground_height + 0.02:
            self.jump_velocity = 8.5
        self.space_was_down = space_down

        if self.player.y > self.ground_height or self.jump_velocity > 0:
            self.jump_velocity -= 22 * dt
            self.player.y = max(
                self.ground_height,
                self.player.y + self.jump_velocity * dt,
            )
            if self.player.y == self.ground_height:
                self.jump_velocity = 0

        self.spawn_elapsed += dt
        spawn_interval = max(0.34, 1.25 - self.elapsed * 0.012)
        if self.challenge_mode:
            spawn_interval = max(0.24, spawn_interval * 0.78)
        if self.spawn_elapsed >= spawn_interval:
            self.spawn_elapsed = 0
            self.spawn_obstacle()

        for obstacle in self.entities[:]:
            entity = obstacle["entity"]
            entity.z -= obstacle["speed"] * dt
            if obstacle["kind"] == "ball":
                entity.rotation_x += obstacle["speed"] * 38 * dt
            if self.collides(obstacle):
                self.finish()
                return
            if entity.z < -10:
                entity.disable()
                self.entities.remove(obstacle)

        camera.position = Vec3(self.player.x * 0.35, 15, -20)
        camera.look_at(Vec3(self.player.x * 0.2, 0, 4))


def quit_app():
    """Close the game window. `application.user_exit` no longer exists in newer Ursina versions."""
    quit_function = getattr(application, "quit", None)
    if quit_function is not None:
        quit_function()
    else:
        sys.exit()


class GameController(Entity):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        self.game.update()

    def input(self, key):
        if key == "escape":
            self.game.save_result()
            quit_app()
        elif key == "r" and self.game.game_over:
            self.game.restart()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-file", required=True)
    parser.add_argument("--challenge-mode", action="store_true")
    args = parser.parse_args(argv)

    app = Ursina()
    window.title = "Lava Escape"
    window.color = rgb(20, 23, 38)
    Sky()
    DirectionalLight().look_at(Vec3(1, -2, -1))

    game = LavaEscape(challenge_mode=args.challenge_mode)
    GameController(game)

    game.result_file = args.result_file
    try:
        app.run()
    finally:
        game.save_result()


if __name__ == "__main__":
    main()