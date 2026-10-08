"""Manages and displays the player's health."""

import time
from dataclasses import dataclass, field

import pygame

from src.entities.items.shield import SHIELD_TIME
from src.resources.texture_atlas import TextureAtlas

from .game_stats import GameStats

INIT_HEARTS: int = 5
MAX_HEARTS: int = 5


@dataclass
class Health:
    """Handles ship health and shields."""

    # Look the display surface up lazily (the lambda runs at instantiation).
    # Binding pygame.display.get_surface directly here would freeze the raw
    # window surface instead of the logical one the game draws on.
    screen: pygame.Surface = field(default_factory=lambda: pygame.display.get_surface(), init=False)
    current_hearts: int = INIT_HEARTS
    freeze_flag: bool = False
    freeze_time: float = 0

    def reset(self) -> None:
        """Reset health to initial value."""
        self.current_hearts = INIT_HEARTS

    def full(self) -> None:
        """Set health to maximum."""
        self.current_hearts = MAX_HEARTS

    def increase(self) -> None:
        """Increase health by one if not at max."""
        if self.current_hearts < MAX_HEARTS:
            self.current_hearts += 1

    def decrease(self, stats: GameStats) -> None:
        """Decrease health by one unless shielded."""
        if self.freeze_flag and time.time() - self.freeze_time < SHIELD_TIME:
            return
        self.current_hearts -= 1
        if self.current_hearts == 0:
            stats.game_active = False
            pygame.mouse.set_visible(True)

    def activate_shield(self) -> None:
        """Activate temporary shield."""
        self.freeze_flag = True
        self.freeze_time = time.time()

    def draw(self) -> None:
        """Draw the health bar in the top-left corner.

        The hearts are drawn a little larger, with a soft drop shadow, so they
        stay readable over the busy starfield background.
        """
        heart_size: tuple[int, int] = (28, 28)
        gap: int = 6
        margin: int = 16

        full_heart: pygame.Surface = pygame.transform.scale(
            TextureAtlas.get_sprite_texture("heart/full_heart.png"),
            heart_size,
        )
        empty_heart: pygame.Surface = pygame.transform.scale(
            TextureAtlas.get_sprite_texture("heart/empty_heart.png"),
            heart_size,
        )

        x: int = margin
        for i in range(MAX_HEARTS):
            heart: pygame.Surface = full_heart if i < self.current_hearts else empty_heart

            # Dark silhouette behind the heart so it reads over bright scenery.
            shadow: pygame.Surface = heart.copy()
            shadow.fill((0, 0, 0, 190), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(shadow, (x + 2, margin + 2))
            self.screen.blit(heart, (x, margin))

            x += heart_size[0] + gap
