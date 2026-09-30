import pygame  # Import pygame for event handling, timing, fonts, and rendering.
from .round import Round  # Import the Round class used to manage individual rounds.


WHITE = (255, 255, 255)  # Define the white color used for text.
BLACK = (0, 0, 0)  # Define the black color.
GRAY = (90, 90, 90)  # Define the grey color used during the waiting state.
GREEN = (40, 180, 90)  # Define the green color used during the GO state.
BLUE = (50, 90, 170)  # Define the blue color used for valid reaction results.
RED = (180, 50, 50)  # Define the red color used when a false start occurs.


class GameEngine:  # Define the main game engine that controls the reaction-time tester.
    def __init__(self, width, height, rounds_total=5, min_wait_ms=1000, max_wait_ms=3000):  # Initialize the game engine.
        self.width = width  # Store the width of the game window.
        self.height = height  # Store the height of the game window.
        self.rounds_total = rounds_total  # Store the number of valid rounds required for the session.
        self.min_wait_ms = min_wait_ms  # Store the minimum random waiting time.
        self.max_wait_ms = max_wait_ms  # Store the maximum random waiting time.
        self.round = Round(self.min_wait_ms, self.max_wait_ms)  # Create the first reaction-time round.
        self.reaction_times = []  # Store only valid reaction times.
        self.result_shown_at = None  # Store when the result or false-start message was shown.
        self.result_pause_ms = 800  # Wait 800 milliseconds before starting the next round.
        self.font = pygame.font.SysFont("Arial", 30)  # Create the normal-sized font.
        self.big_font = pygame.font.SysFont("Arial", 46)  # Create the large font.
        self.game_over = False  # Track whether the entire session has finished.

    def handle_event(self, event):  # Handle mouse and keyboard events.
        if self.game_over:  # Ignore input after the session has ended.
            return  # Exit the function without processing the event.
        is_click = event.type == pygame.MOUSEBUTTONDOWN  # Check whether the event is a mouse click.
        is_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE  # Check whether the event is a Space key press.
        if is_click or is_space:  # Process either a mouse click or Space key press.
            reaction_ms = self.round.register_input()  # Ask the current round to process the input.
            if reaction_ms is not None:  # Only continue when a valid reaction time was produced.
                self.reaction_times.append(reaction_ms)  # Add the valid reaction time to the session results.
            if self.round.state in ("result", "false_start"):  # Start the result pause for either a valid reaction or false start.
                self.result_shown_at = pygame.time.get_ticks()  # Record when the result message became active.

    def handle_input(self):  # Handle continuously-held input if it is ever needed.
        pass  # No continuous input is required because clicks and Space presses are handled as events.

    def update(self):  # Update the game state every frame.
        if self.game_over:  # Stop updating when the session has ended.
            return  # Exit the update function.
        self.round.update()  # Update the current round and potentially transition from waiting to GO.
        if self.round.state in ("result", "false_start"):  # Check whether the round has finished or a false start occurred.
            now = pygame.time.get_ticks()  # Get the current pygame time.
            if now - self.result_shown_at >= self.result_pause_ms:  # Check whether the short result pause has finished.
                self._start_next_round()  # Start the next round.

    def _start_next_round(self):  # Start a new round or end the session when enough valid reactions exist.
        if len(self.reaction_times) >= self.rounds_total:  # Check whether the required number of valid reactions has been recorded.
            self.game_over = True  # Mark the complete session as finished.
            return  # Stop here instead of creating another round.
        self.round = Round(self.min_wait_ms, self.max_wait_ms)  # Create a fresh round with a new random waiting delay.

    def average_reaction_ms(self):  # Calculate the average of all valid reaction times.
        if not self.reaction_times:  # Check whether there are currently no valid reaction times.
            return 0  # Return zero when there are no values to average.
        return round(sum(self.reaction_times) / len(self.reaction_times))  # Calculate and round the average reaction time.

    def render(self, screen):  # Draw the current game state onto the pygame screen.
        if self.round.state == "waiting":  # Check whether the player is currently waiting for the green signal.
            bg = GRAY  # Use the grey background during the waiting state.
            message = "Wait for green..."  # Tell the player to wait.
        elif self.round.state == "go":  # Check whether the player can react.
            bg = GREEN  # Use the green background during the GO state.
            message = "Click now!"  # Tell the player to react.
        elif self.round.state == "false_start":  # Check whether the player clicked too early.
            bg = RED  # Use a red background to indicate the false start.
            message = "False start!"  # Tell the player that the input happened too early.
        else:  # Handle the normal result state.
            bg = BLUE  # Use the blue background for a valid reaction result.
            message = f"{self.round.reaction_ms} ms"  # Display the valid reaction time.

        screen.fill(bg)  # Fill the entire screen with the selected background color.

        text_surf = self.big_font.render(message, True, WHITE)  # Render the main state message in white.
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))  # Center the main message in the window.
        screen.blit(text_surf, text_rect)  # Draw the main message onto the screen.

        round_num = min(len(self.reaction_times) + 1, self.rounds_total)  # Calculate the current round number based only on valid reactions.
        round_text = self.font.render(f"Round {round_num}/{self.rounds_total}", True, WHITE)  # Render the round counter.
        screen.blit(round_text, (10, 10))  # Draw the round counter in the top-left corner.

        avg_text = self.font.render(f"Avg: {self.average_reaction_ms()} ms", True, WHITE)  # Render the current average reaction time.
        screen.blit(avg_text, (self.width - 190, 10))  # Draw the average in the top-right area.

        if self.game_over and not getattr(self, "_game_over_logged", False):  # Check whether the session just finished and has not been logged yet.
            print("Session complete! Reaction times (ms):", self.reaction_times)  # Print the final reaction times to the terminal.
            print("Average:", self.average_reaction_ms(), "ms")  # Print the final average to the terminal.
            self._game_over_logged = True  # Prevent the final results from being printed repeatedly.