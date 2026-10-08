import time
import pygame
from src.settings import Settings
from src.resources.texture_atlas import TextureAtlas

settings = Settings()


class Animation:
    def __init__(self, frame_path, frame_count, screen, latency=0.001, divider=4, visibility=True, alpha=100):
        self.settings = Settings()
        self.animation_frames = []
        self.animation_rects = []
        self.screen = screen

        self.animation_visibility = visibility

        self.animation_position_x = 0
        self.animation_position_y = 0

        self.animation_latency = latency

        # Time based animations variables
        self.timer_status = False
        self.animation_duration = 0
        self.animation_started_time = 0
        self.terminate_sound = None

        temp_path = frame_path
        for i in range(1, frame_count + 1):
            temp_path = temp_path + f"/f{i}.png"
            loaded_frame = TextureAtlas.get_animation_frame(temp_path)
            loaded_frame = pygame.transform.scale(loaded_frame, (loaded_frame.get_width() / divider,
                                                                 loaded_frame.get_height() / divider))
            loaded_frame.set_alpha(alpha)
            self.animation_frames.append(loaded_frame)
            self.animation_rects.append((loaded_frame.get_rect()))
            temp_path = frame_path  # reset to actual path.

    def set_position(self, x, y):
        self.animation_position_x = x
        self.animation_position_y = y

    def set_visibility(self, visibility, timer=False, duration=10, terminate_sound=None):
        self.animation_visibility = visibility
        if timer:
            self.timer_status = True
            self.animation_duration = duration
            self.animation_started_time = time.time()
            self.terminate_sound = terminate_sound

    def play(self):
        if self.animation_visibility:
            if self.timer_status:
                elapsed_play_time = time.time() - self.animation_started_time
                if elapsed_play_time >= self.animation_duration:
                    self.set_visibility(False)
                    if self.terminate_sound:
                        self.terminate_sound.play()
            i = 0
            for frame in self.animation_frames:
                current_rect = self.animation_rects[i]
                current_rect.x = self.animation_position_x
                current_rect.y = self.animation_position_y
                self.screen.blit(frame, current_rect)
                i += 1
                # Presentation is handled once per frame by display.present();
                # a partial display.update() here used logical rects that may
                # fall outside a monitor-fitted window.
                time.sleep(self.animation_latency)  # TODO: Find a better and faster solution.
