import pygame
import logging
import os

from pathlib import Path

from .. import settings

class TextureAtlas:
    __sprites_folder: Path = settings.ASSETS_DIR / "sprites"
    __animations_folder: Path = settings.ASSETS_DIR / "animations"
    __sprites_atlas_max_width = 2048
    __animations_atlas_max_width = 8192
    __loaded: bool = False

    __sprites_atlas_mappings: dict[str, dict] = {}
    __sprites_atlas_surface: pygame.Surface
    __animations_atlas_mappings: dict[str, dict] = {}
    __animations_atlas_surface: pygame.Surface

    __logger = logging.getLogger(__name__)

    @staticmethod
    def initialize() -> None:
        """The initializer of TextureAtlas. This method should only call once at the beginning after
        pygame.screen.set_mode() called"""

        if TextureAtlas.__loaded:
            return

        TextureAtlas.__init_sprites()
        TextureAtlas.__init_animations()

        TextureAtlas.__loaded = True

    @staticmethod
    def __init_sprites():
        TextureAtlas.__logger.info("Start loading sprite textures...")

        sprite_files = [os.path.join(root, file) for root, dirs, files in os.walk(TextureAtlas.__sprites_folder) for
                        file in files if file.endswith(".png")]

        sprites: list[tuple[str, pygame.Surface, int, int]] = []
        for file in sprite_files:
            image = pygame.image.load(file).convert_alpha()
            width, height = image.get_size()
            sprites.append((Path(file).relative_to(TextureAtlas.__sprites_folder).as_posix(), image, width, height))

        # Arrange and measure sprites atlas size
        x, y, = 0, 0
        row_height = 0

        atlas_width = TextureAtlas.__sprites_atlas_max_width
        atlas_height = 0

        padding = 2

        for path, image, w, h in sprites:
            if x + w > atlas_width:
                x = 0
                y += row_height + padding

            TextureAtlas.__sprites_atlas_mappings[path] = {"x": x, "y": y, "width": w, "height": h}

            x += w + padding
            row_height = max(row_height, h)

        atlas_height = y + row_height

        # Create and fill the sprites atlas
        TextureAtlas.__sprites_atlas_surface = pygame.Surface((atlas_width, atlas_height), pygame.SRCALPHA)
        for name, image, _, _ in sprites:
            x = TextureAtlas.__sprites_atlas_mappings.get(name).get("x")
            y = TextureAtlas.__sprites_atlas_mappings.get(name).get("y")
            TextureAtlas.__sprites_atlas_surface.blit(image, (x, y))

        TextureAtlas.__logger.info("Sprite textures loading finished")

    @staticmethod
    def __init_animations():
        TextureAtlas.__logger.info("Start loading animations...")

        animations_files = [os.path.join(root, file) for root, dirs, files in os.walk(TextureAtlas.__animations_folder)
                            for file in files if file.endswith(".png")]

        grouped_animations: dict[str, list[tuple[str, pygame.Surface, int, int]]] = {}
        for file in animations_files:
            image = pygame.image.load(file).convert_alpha()
            width, height = image.get_size()

            file = Path(file).relative_to(TextureAtlas.__animations_folder).as_posix()
            group = file.split("/")[0]
            frame = file.split("/")[1]

            if group in grouped_animations.keys():
                curr_group = grouped_animations.get(group)
                curr_group.append((frame, image, width, height))
                grouped_animations[group] = curr_group
            else:
                grouped_animations[group] = [(frame, image, width, height)]

        # print(enumerate(grouped_animations))

        # Arrange and measure animations atlas size
        x, y = 0, 0
        row_height = 0

        atlas_width = TextureAtlas.__animations_atlas_max_width
        atlas_height = 0

        padding = 2

        for index, (group, frames) in enumerate(grouped_animations.items()):
            for frame in frames:
                file, image, w, h = frame

                if x + w > atlas_width:
                    x = 0
                    y += row_height + padding

                TextureAtlas.__animations_atlas_mappings[f"{group}/{file}"] = {"x": x, "y": y, "width": w, "height": h}

                x += w + padding
                row_height = max(row_height, h)

        atlas_height = y + row_height

        # Create and fill animations atlas
        TextureAtlas.__animations_atlas_surface = pygame.Surface((atlas_width, atlas_height), pygame.SRCALPHA)
        for index, (group, frames) in enumerate(grouped_animations.items()):
            for frame in frames:
                file, image, _, _ = frame

                x = TextureAtlas.__animations_atlas_mappings.get(f"{group}/{file}").get("x")
                y = TextureAtlas.__animations_atlas_mappings.get(f"{group}/{file}").get("y")
                TextureAtlas.__animations_atlas_surface.blit(image, (x, y))

        TextureAtlas.__logger.info("Animation loading finished")

    @staticmethod
    def get_sprite_texture(path: str) -> pygame.Surface | None:
        """This method will return a sprite texture. Returns None, if sprite texture wasn't present."""
        if TextureAtlas.__loaded:
            if not path.endswith(".png"):
                path += ".png"
            if path in TextureAtlas.__sprites_atlas_mappings.keys():
                texture_mappings = TextureAtlas.__sprites_atlas_mappings.get(path)
                return TextureAtlas.__sprites_atlas_surface.subsurface(pygame.Rect(texture_mappings.get("x"), texture_mappings.get("y"),
                                                                                   texture_mappings.get("width"), texture_mappings.get("height")))
            else:
                TextureAtlas.__logger.error(f"Sprite {path} doesn't exist")
                return None
        else:
            TextureAtlas.__logger.error("Sprite textures are not loaded")
            return None

    @staticmethod
    def get_animation_frame(path: str) -> pygame.Surface | None:
        """This method will return an animation frame. Returns None, if animation frame wasn't present."""
        if TextureAtlas.__loaded:
            if not path.endswith(".png"):
                path += ".png"
            if path in TextureAtlas.__animations_atlas_mappings.keys():
                texture_mappings = TextureAtlas.__animations_atlas_mappings.get(path)
                return TextureAtlas.__animations_atlas_surface.subsurface(pygame.Rect(texture_mappings.get("x"), texture_mappings.get("y"),
                                                                                   texture_mappings.get("width"), texture_mappings.get("height")))
            else:
                TextureAtlas.__logger.error(f"Animation frame {path} doesn't exist")
                return None
        else:
            TextureAtlas.__logger.error("Animations are not loaded")
            return None

    @staticmethod
    def save_to_file() -> None:
        """This method will create two image files, one for sprites atlas, and another one for animations atlas. This
        method is only for debugging purposes."""
        pygame.image.save(TextureAtlas.__sprites_atlas_surface, "atlas-sprites.png")
        pygame.image.save(TextureAtlas.__sprites_atlas_surface, "atlas-animations.png")
