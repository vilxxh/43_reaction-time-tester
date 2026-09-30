import random  # Import random so that we can generate an unpredictable waiting time.
import pygame  # Import pygame so that we can use its timing functions.


class Round:  # Define the Round class, which manages one reaction-time round.
    def __init__(self, min_wait_ms=1000, max_wait_ms=3000):  # Initialize a new round with configurable wait limits.
        self.wait_delay_ms = random.randint(min_wait_ms, max_wait_ms)  # Choose a random waiting delay between the minimum and maximum values.
        self.state = "waiting"  # Start the round in the grey waiting state.
        self.start_time = pygame.time.get_ticks()  # Record when the round itself starts.
        self.go_time = None  # There is no GO time yet because the screen has not turned green.
        self.reaction_ms = None  # There is no reaction time yet because the player has not reacted.
        self.false_start = False  # Track whether the player made a false start during the waiting phase.

    def update(self):  # Update the state of the current round.
        if self.state == "waiting":  # Only check the waiting timer while the round is waiting for the GO signal.
            now = pygame.time.get_ticks()  # Get the current pygame time in milliseconds.
            if now - self.start_time >= self.wait_delay_ms:  # Check whether the random waiting period has finished.
                self.state = "go"  # Change the state to GO so the screen becomes green.
                self.go_time = now  # Record the exact moment the GO state begins.

    def register_input(self):  # Process a mouse click or Space key press from the player.
        now = pygame.time.get_ticks()  # Get the exact time at which the input occurred.
        if self.state == "waiting":  # Check whether the player reacted before the screen turned green.
            self.false_start = True  # Mark this round as a false start.
            self.state = "false_start"  # Change the state so the game can display the false-start result.
            return None  # Return None because this is not a valid reaction time.
        if self.state == "go":  # Only calculate a reaction time when the round is in the GO state.
            self.reaction_ms = now - self.go_time  # Calculate reaction time from the exact moment the screen turned green.
            self.state = "result"  # Change the state to result after receiving a valid reaction.
            return self.reaction_ms  # Return the valid reaction time to the game engine.
        return None  # Ignore any input that occurs after the round has already finished.