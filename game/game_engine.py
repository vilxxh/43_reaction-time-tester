import pygame
import math
import array
from .round import Round

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (180, 50, 50)


class GameEngine:
    def __init__(self, width, height, rounds_total=5, min_wait_ms=1000, max_wait_ms=3000):
        self.width = width
        self.height = height

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.round = Round(self.min_wait_ms, self.max_wait_ms)
        self.reaction_times = []

        self.result_shown_at = None
        self.result_pause_ms = 800

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.game_over = False
        self.replay_menu = False

        self.sound_enabled = False
        self.go_sound = None
        self.false_start_sound = None
        self.game_over_sound = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.go_sound = self._create_tone(880, 120)
            self.false_start_sound = self._create_tone(220, 250)
            self.game_over_sound = self._create_tone(440, 400)

            self.sound_enabled = True
        except pygame.error:
            self.sound_enabled = False

    def _create_tone(self, frequency, duration_ms):
        sample_rate = 44100
        sample_count = int(sample_rate * duration_ms / 1000)

        buffer = array.array("h")
        amplitude = 16000

        for i in range(sample_count):
            value = int(
                amplitude
                * math.sin(
                    2 * math.pi * frequency * i / sample_rate
                )
            )
            buffer.append(value)

        return pygame.mixer.Sound(buffer=buffer)

    def _play_sound(self, sound):
        if self.sound_enabled and sound is not None:
            sound.play()

    def handle_event(self, event):
        if self.replay_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_new_game(3, 2000, 4000)

                elif event.key == pygame.K_2:
                    self._start_new_game(5, 1000, 3000)

                elif event.key == pygame.K_3:
                    self._start_new_game(7, 500, 2000)

                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(
                        pygame.event.Event(pygame.QUIT)
                    )

            return

        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.replay_menu = True

            return

        is_click = event.type == pygame.MOUSEBUTTONDOWN

        is_space = (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        )

        if is_click or is_space:
            reaction_ms = self.round.register_input()

            if self.round.state == "false_start":
                self._play_sound(self.false_start_sound)

            elif reaction_ms is not None:
                self.reaction_times.append(reaction_ms)

            if self.round.state in ("result", "false_start"):
                self.result_shown_at = pygame.time.get_ticks()

    def handle_input(self):
        pass

    def update(self):
        if self.game_over or self.replay_menu:
            return

        previous_state = self.round.state

        self.round.update()

        if (
            previous_state == "waiting"
            and self.round.state == "go"
        ):
            self._play_sound(self.go_sound)

        if self.round.state in ("result", "false_start"):
            now = pygame.time.get_ticks()

            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_next_round(self):
        if len(self.reaction_times) >= self.rounds_total:
            self.game_over = True
            self._play_sound(self.game_over_sound)
            return

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

    def _start_new_game(
        self,
        rounds_total,
        min_wait_ms,
        max_wait_ms
    ):
        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.reaction_times = []

        self.game_over = False
        self.replay_menu = False
        self.result_shown_at = None

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0

        return round(
            sum(self.reaction_times)
            / len(self.reaction_times)
        )

    def render(self, screen):
        if self.replay_menu:
            self._render_replay_menu(screen)
            return

        if self.game_over:
            self._render_game_over(screen)
            return

        if self.round.state == "waiting":
            bg = GRAY
            message = "Wait for green..."

        elif self.round.state == "go":
            bg = GREEN
            message = "Click now!"

        elif self.round.state == "false_start":
            bg = RED
            message = "False start!"

        else:
            bg = BLUE
            message = f"{self.round.reaction_ms} ms"

        screen.fill(bg)

        text_surf = self.big_font.render(
            message,
            True,
            WHITE
        )

        text_rect = text_surf.get_rect(
            center=(
                self.width // 2,
                self.height // 2
            )
        )

        screen.blit(
            text_surf,
            text_rect
        )

        round_num = min(
            len(self.reaction_times) + 1,
            self.rounds_total
        )

        round_text = self.font.render(
            f"Round {round_num}/{self.rounds_total}",
            True,
            WHITE
        )

        screen.blit(
            round_text,
            (10, 10)
        )

        avg_text = self.font.render(
            f"Avg: {self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        screen.blit(
            avg_text,
            (self.width - 190, 10)
        )

    def _render_game_over(self, screen):
        screen.fill(BLACK)

        title = self.big_font.render(
            "GAME OVER",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(self.width // 2, 40)
        )

        screen.blit(title, title_rect)

        results_title = self.font.render(
            "Reaction Times",
            True,
            WHITE
        )

        results_rect = results_title.get_rect(
            center=(self.width // 2, 82)
        )

        screen.blit(results_title, results_rect)

        start_y = 115
        line_spacing = 27

        for index, reaction_time in enumerate(self.reaction_times):
            result_text = self.small_font.render(
                f"Round {index + 1}: {reaction_time} ms",
                True,
                WHITE
            )

            result_rect = result_text.get_rect(
                center=(
                    self.width // 2,
                    start_y + index * line_spacing
                )
            )

            screen.blit(
                result_text,
                result_rect
            )

        average_y = (
            start_y
            + len(self.reaction_times) * line_spacing
            + 12
        )

        average_text = self.font.render(
            f"Average: {self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        average_rect = average_text.get_rect(
            center=(
                self.width // 2,
                average_y
            )
        )

        screen.blit(
            average_text,
            average_rect
        )

        continue_text = self.small_font.render(
            "Press SPACE to continue",
            True,
            WHITE
        )

        continue_rect = continue_text.get_rect(
            center=(
                self.width // 2,
                375
            )
        )

        screen.blit(
            continue_text,
            continue_rect
        )

    def _render_replay_menu(self, screen):
        screen.fill(BLACK)

        title = self.big_font.render(
            "PLAY AGAIN?",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                80
            )
        )

        screen.blit(
            title,
            title_rect
        )

        easy = self.font.render(
            "1 - Easy",
            True,
            WHITE
        )

        medium = self.font.render(
            "2 - Medium",
            True,
            WHITE
        )

        hard = self.font.render(
            "3 - Hard",
            True,
            WHITE
        )

        exit_text = self.font.render(
            "ESC - Exit",
            True,
            WHITE
        )

        screen.blit(easy, (230, 150))
        screen.blit(medium, (230, 200))
        screen.blit(hard, (230, 250))
        screen.blit(exit_text, (230, 310))