import pygame
import logging
from dataclasses import dataclass, field

from . import settings
from .settings import ASSETS_DIR


DIR = ASSETS_DIR / "background"


@dataclass
class Region:
    """Represents a region in the game.
        Attributes:
            region_name (str): Region name.
            background_name (str): Background path in the background directory.
            min_score (int): Minimum score this region require.
            size (tuple[int, int]): Region background size
    """

    region_name: str
    background_name: str
    min_score: int
    size: tuple[int, int]

    logger: logging.Logger = field(init=False)
    background: pygame.Surface = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

        try:
            image: pygame.Surface = pygame.image.load(DIR / self.background_name).convert()
            self.background = pygame.transform.scale(image, self.size)
        except FileNotFoundError:
            self.logger.error(f"Background image not found: {DIR / self.background_name}'")
            self.background = pygame.transform.scale(pygame.image.load(DIR / "starfield/1.png").convert(), self.size)


class RegionManager:
    """A class to manage regions."""

    def __init__(self, screen_size: tuple[int, int],  *regions: Region) -> None:
        self.regions: list[Region] = sorted(regions, key=lambda r: r.min_score)  # Sort regions by their minimum score required
        self.current_region_index: int = 0

        self.__last_region_index: int = len(self.regions) - 1
        self.__y: float = -self.regions[self.current_region_index].background.get_height()  # Background scroll y

        # Backgrounds to draw
        # First element of each tuple is the background and the second element is a flag to determine if it requires fade effect or not
        self.__to_draw: list[tuple[pygame.Surface, bool]] = [(self.regions[self.current_region_index].background, False) for _ in range(2)]

        # Fade effect attributes
        self.__fade_surface: pygame.Surface = pygame.Surface(screen_size)
        self.__fade_surface.fill((0, 0, 0))
        self.__fade_alpha: int = 0
        self.__fading: bool = False
        self.__fade_direction: float = 1  # 1 = fade out | -1 = fade in

    def can_spawn_objects(self) -> bool:
        return not (self.__fading and self.__to_draw[1][1])

    def reset(self) -> None:
        self.current_region_index = 0
        self.__y: float = -self.regions[self.current_region_index].background.get_height()
        self.__to_draw: list[tuple[pygame.Surface, bool]] = [(self.regions[self.current_region_index].background, False) for _ in range(2)]

    def update_current_region(self, score: int) -> None:
        """Update current region index base on the player score and fade state.
            Args:
                score (int): Player score.
        """
        if self.current_region_index + 1 <= self.__last_region_index:
            if score >= self.regions[self.current_region_index + 1].min_score and not self.__fading:
                self.current_region_index += 1
                self.__start_fade()

    def get_current_region(self) -> Region:
        """Returns the current region.
            Returns:
                Region: Current region.
        """
        return self.regions[self.current_region_index]

    def update(self, screen: pygame.Surface, score: int, dt: float) -> None:
        self.update_current_region(score)
        current_region_height: int = self.get_current_region().background.get_height()

        self.__draw(screen, current_region_height, dt)
        self.__update_y(current_region_height, dt)

    def __draw(self, screen: pygame.Surface, bg_height: int, dt: float) -> None:
        screen.fill((0, 0, 0))
        screen.blit(self.__to_draw[0][0], (0, bg_height + self.__y))
        screen.blit(self.__to_draw[1][0], (0, self.__y))

        # Draw fade overlay
        if self.__fading and self.__to_draw[1][1]:
            self.__update_fade(dt)

            # Overlay
            self.__fade_surface.set_alpha(self.__fade_alpha)
            screen.blit(self.__fade_surface, (0, 0))

            # Overlay text
            text_surface: pygame.Surface = settings.FONT.render(f"Entering: {self.get_current_region().region_name}",
                                                                True, (255, 255, 255))
            text_surface.set_alpha(self.__fade_alpha)
            text_rect: pygame.Rect = text_surface.get_rect(center=screen.get_rect().center)

            screen.blit(text_surface, text_rect)

    def __update_y(self, bg_height: int, dt: float) -> None:
        if self.__y > 0:
            next_bg: pygame.Surface = self.get_current_region().background

            # Checks if next region is the same as current region or not
            # If it wasn't, mark it as True to do a fade effect
            fade_flag: bool = False if next_bg == self.__to_draw[1][0] else True

            # Shift backgrounds
            self.__to_draw = [self.__to_draw[1], (next_bg, fade_flag)]

            self.__y = -bg_height
        self.__y += 0.7 * dt

    def __start_fade(self) -> None:
        self.__fading = True
        self.__fade_direction = 1
        self.__fade_alpha = 0

    def __update_fade(self, dt: float) -> None:
        self.__fade_alpha += 1.5 * self.__fade_direction * dt

        if self.__fade_alpha >= 255:
            self.__fade_alpha = 255
            self.__fade_direction = -1
            # Change the background when it was all black
            self.__to_draw[0] = (self.get_current_region().background, False)
        elif self.__fade_alpha <= 0:
            self.__fade_alpha = 0
            self.__fading = False
