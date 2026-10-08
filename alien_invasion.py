import logging
import pygame
from pygame.sprite import Group

import src.display as display
import src.game_functions as gf
from src.entities.ui.elements.button import Button as btn
from src.entities.ui.elements.scoreboard import Scoreboard
from src.resources.texture_atlas import TextureAtlas
from src.game_functions import generate_heart
from src.game_stats import GameStats
from src.health import Health
from src.input import Input
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH, Settings
from src.ship import Ship
from src.log_manager import LogManager
from src.region import Region, RegionManager
from src.rl import init_autopilot, init_controller



def init_regions(screen: pygame.Surface) -> RegionManager:
    size: tuple[int, int] = screen.get_size()

    return RegionManager(size,
        Region("Starfield Stage - 1", "starfield/1.png", 0, size),
        Region("Starfield Stage - 2", "starfield/2.png", 200, size),
        Region("Starfield Stage - 3", "starfield/3.png", 400, size),
        Region("Starfield Stage - 4", "starfield/4.png", 600, size),
        Region("Starfield Stage - 5", "starfield/5.png", 800, size),
        Region("Verdant Expanse Stage - 1", "verdant expanse/1.png", 1100, size),
        Region("Verdant Expanse Stage - 2", "verdant expanse/2.png", 1400, size),
        Region("Verdant Expanse Stage - 3", "verdant expanse/3.png", 1700, size),
        Region("Verdant Expanse Stage - 4", "verdant expanse/4.png", 2000, size),
        Region("Verdant Expanse Stage - 5", "verdant expanse/5.png", 2300, size),
        Region("Violet Void Stage - 1", "violet void/1.png", 2700, size),
        Region("Violet Void Stage - 2", "violet void/2.png", 3100, size),
        Region("Violet Void Stage - 3", "violet void/3.png", 3500, size),
        Region("Violet Void Stage - 4", "violet void/4.png", 3900, size),
        Region("Violet Void Stage - 5", "violet void/5.png", 4300, size)
    )

def run_game():
    LogManager.init()
    pygame.init()

    logger = logging.getLogger(__name__)

    logger.info("Starting game...")

    ai_settings = Settings()

    # Keep the fixed 1200x800 logical resolution but size the actual window so
    # it always fits on the monitor (never runs off the screen).
    window_size = display.fit_window_size((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen: pygame.Surface = display.init(window_size, (SCREEN_WIDTH, SCREEN_HEIGHT))

    input = Input()

    TextureAtlas.initialize()

    # Load the pre-trained Q-learning policy for the enemies (see train_rl.py).
    rl_controller = init_controller()
    if rl_controller.enabled:
        logger.info(
            "RL enemy policy active (movement: %d states, fire: %d states)",
            len(rl_controller.movement),
            len(rl_controller.fire),
        )
    else:
        logger.warning("RL Q-tables not found - run 'python train_rl.py' to train the enemies")

    # Load the pre-trained auto-pilot for the player's ship (see train_ship.py).
    ship_autopilot = init_autopilot()
    if ship_autopilot.movement_enabled and ship_autopilot.fire_enabled:
        logger.info(
            "Ship auto-pilot active (movement: %d states, fire: %d states)",
            len(ship_autopilot.movement),
            len(ship_autopilot.fire),
        )
    else:
        logger.warning("Ship RL Q-tables not found - run 'python train_ship.py' to train the auto-pilot")

    logger.info("Initializing region manager")
    region_manager: RegionManager = init_regions(screen)

    pygame.display.set_caption("Alien Invasion")

    clock = pygame.time.Clock()
    alien_spawn_timer = pygame.time.get_ticks()

    # Create an instance to store game statistics and create scoreboard.
    stats = GameStats()
    sb = Scoreboard(screen, stats)

    health = Health()
    health.reset()

    # Make a ship, and a group for each game sprite.
    ship = Ship(input)
    bullets = Group()
    aliens = Group()
    cargoes = Group()
    alien_bullets = Group()
    hearts = Group()
    shields = Group()

    play_button = btn(
        "start",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + -74),
        lambda: gf.run_play_button(ai_settings, stats, ship, aliens, cargoes, bullets, health, region_manager, sb),
        lambda: not stats.game_active and not stats.credits_active,
    )

    credits_button = btn(
        "Credits",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + 10),
        lambda: gf.run_credit_button(stats),
        lambda: not stats.credits_active and not stats.game_active,
    )

    back_button = btn(
        "Back",
        (240, 64),
        (10, 50),
        lambda: gf.run_back_button(stats),
        lambda: stats.credits_active,
    )

    # RL auto-pilot toggle: one button, two mutually exclusive states.
    auto_on_button = btn(
        "Auto: OFF",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + 94),
        lambda: setattr(stats, "auto_mode", True),
        lambda: not stats.auto_mode and not stats.game_active and not stats.credits_active,
    )

    auto_off_button = btn(
        "Auto: ON",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + 94),
        lambda: setattr(stats, "auto_mode", False),
        lambda: stats.auto_mode and not stats.game_active and not stats.credits_active,
    )

    # Enemy AI toggle: RL-trained policy vs. the classic chase-and-random-fire.
    # Same convention as the Auto pair: the label shows the current mode and
    # clicking it flips to the other one.
    rl_on_button = btn(
        "AI: RL",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + 178),
        lambda: setattr(stats, "rl_enemies", False),
        lambda: stats.rl_enemies and not stats.game_active and not stats.credits_active,
    )

    rl_off_button = btn(
        "AI: Classic",
        (240, 64),
        (screen.get_rect().centerx - 120, screen.get_rect().centery + 178),
        lambda: setattr(stats, "rl_enemies", True),
        lambda: not stats.rl_enemies and not stats.game_active and not stats.credits_active,
    )

    alien_spawn_counter = 0

    gf.load_animations(screen)
    gf.load_credits()

    logger.info("Game started")

    # Start the main loop for the game.
    while True:
        input.update()
        gf.check_events(ai_settings, input, screen, stats, ship, bullets)
        if stats.game_active:
            # Prevent mouse from going out of screen.
            pygame.event.set_grab(True)

            # Update game sprites
            gf.update_game_sprites(
                ai_settings,
                screen,
                stats,
                sb,
                ship,
                aliens,
                bullets,
                cargoes,
                alien_bullets,
                health,
                hearts,
                shields,
            )
        else:
            pygame.event.set_grab(False)

        gf.update_screen(
            region_manager,
            ai_settings,
            screen,
            stats,
            sb,
            ship,
            aliens,
            bullets,
            play_button,
            credits_button,
            back_button,
            auto_on_button,
            auto_off_button,
            rl_on_button,
            rl_off_button,
            cargoes,
            alien_bullets,
            health,
            hearts,
            shields,
        )

        clock.tick(ai_settings.fps)

        # Aliens fire timer
        current_time = pygame.time.get_ticks()

        if region_manager.can_spawn_objects():
            if current_time - alien_spawn_timer > 100:
                gf.alien_fire(ai_settings, stats, screen, aliens, alien_bullets, ship)

                generate_heart(stats, screen, hearts)
                gf.generate_shields(screen, ai_settings, stats, shields)

                if alien_spawn_counter % 10 == 0:
                    gf.spawn_random_alien(ai_settings, screen, aliens)

                alien_spawn_counter += 1
                alien_spawn_timer = current_time
        else:
            bullets.empty()
            aliens.empty()
            alien_bullets.empty()
            cargoes.empty()
            hearts.empty()
            shields.empty()


run_game()
