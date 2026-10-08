import math
from abc import ABC, abstractmethod

import pygame
from pygame.sprite import Sprite

from src.resources.texture_atlas import TextureAtlas

from . import settings


class Bullet(ABC, Sprite):
    """An abstract class to create bullets."""

    def __init__(self, target, source, color, speed_factor):
        super(Bullet, self).__init__()
        self.screen: pygame.Surface = pygame.display.get_surface()

        # Load and scale bullet image
        self.image: pygame.Surface = TextureAtlas.get_sprite_texture("bullet/golden_bullet.png")
        self.image_size: tuple[int, int] = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.image_size[0] * 0.03, self.image_size[1] * 0.03))
        self.rect = self.image.get_rect()

        # Set angle and initial position
        self.angle, self.rect.centerx, self.rect.centery = self.set_angle(source, target)

        # Store the bullet's position as a decimal value
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.color = color
        self.speed_factor = speed_factor

    def update(self):
        """Move the bullet with ship's or alien's angle"""

        # Update the decimal position of the bullet.

        self.x -= math.sin(self.angle) * self.speed_factor * settings.DELTA_TIME
        self.y -= math.cos(self.angle) * self.speed_factor * settings.DELTA_TIME

        # Update the rect position
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        """Draw the bullet to the screen."""
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        rotated_rec = rotated_image.get_rect(center=(self.rect.centerx, self.rect.centery))
        self.screen.blit(rotated_image, rotated_rec)

    @abstractmethod
    def set_angle(self, source, target):
        """Set the angle and initial position of the bullet."""
        pass


class ShipBullet(Bullet):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ship):
        super().__init__(None, ship, settings.BULLET_COLOR, settings.BULLET_SPEED_FACTOR)

    def set_angle(self, source, target):
        angle = source.angle  # Use ship's current angle
        x = source.rect.centerx + math.sin(angle) * 30
        y = source.rect.centery - math.cos(angle) * 30
        return angle, x, y


class AlienBullet(Bullet):
    """A class to manage bullets fired from the aliens."""

    def __init__(self, alien, ship, lead: tuple[float, float] = (0.0, 0.0)):
        # Estimated target velocity in pixels per frame. When provided, the
        # bullet is aimed at an intercept point instead of the current
        # position, so it can hit a moving ship.
        self.lead = lead
        super().__init__(ship, alien, settings.BULLET_COLOR, settings.BULLET_SPEED_FACTOR)

    def set_angle(self, source, target):
        bullet_speed = settings.BULLET_SPEED_FACTOR * settings.DELTA_TIME
        flight_time = (
            math.hypot(target.rect.centerx - source.rect.centerx, target.rect.centery - source.rect.centery)
            / max(bullet_speed, 0.001)
        )

        aim_x = target.rect.centerx + self.lead[0] * flight_time
        aim_y = target.rect.centery + self.lead[1] * flight_time

        dx = aim_x - source.rect.centerx
        dy = aim_y - source.rect.centery

        # NOTE: the original code subtracted the literal 90 (radians!), which
        # deflected every alien bullet ~27 degrees off its target.
        angle = math.atan2(-dy, dx) - math.pi / 2

        x = source.rect.centerx
        y = source.rect.centery

        return angle, x, y
