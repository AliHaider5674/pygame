import pygame
import random
import sys
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FPS = 60
GRAVITY = 1
JUMP_FORCE = -15
SCROLL_SPEED = 5
GROUND_HEIGHT = 50
MAX_SNOWFLAKES = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Geometry Dash Clone')
clock = pygame.time.Clock()

# Load images
try:
    background_img = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background_img.fill((20, 20, 50))  # Dark blue background
    
    ground_img = pygame.Surface((WINDOW_WIDTH, GROUND_HEIGHT))
    ground_img.fill((100, 70, 20))  # Brown ground
    
    # Create a simple pattern on the ground
    for i in range(0, WINDOW_WIDTH, 30):
        pygame.draw.line(ground_img, (120, 90, 40), (i, 0), (i, GROUND_HEIGHT), 2)
except:
    print("Error loading images, using simple graphics instead")

# Game states
PLAYING = 0
GAME_OVER = 1

class Snowflake:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(-50, 0)
        self.size = random.randint(1, 4)
        self.speed = random.uniform(1, 3)
        self.wind = random.uniform(-0.5, 0.5)
        
    def update(self):
        self.y += self.speed
        self.x += self.wind
        
        # Reset if off screen
        if self.y > WINDOW_HEIGHT or self.x < 0 or self.x > WINDOW_WIDTH:
            self.x = random.randint(0, WINDOW_WIDTH)
            self.y = random.randint(-50, -10)
            self.wind = random.uniform(-0.5, 0.5)
            
    def draw(self):
        pygame.draw.circle(window, WHITE, (int(self.x), int(self.y)), self.size)

class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 100
        self.y = WINDOW_HEIGHT - GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.color = BLUE
        self.score = 0
        self.speed_multiplier = 1
        self.speed_timer = 0
        self.ghost_mode = False
        self.ghost_timer = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_FORCE
            self.is_jumping = True
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Check ground collision
        if self.y > WINDOW_HEIGHT - GROUND_HEIGHT - self.height:
            self.y = WINDOW_HEIGHT - GROUND_HEIGHT - self.height
            self.velocity_y = 0
            self.is_jumping = False
        
        # Update speed multiplier timer
        if self.speed_multiplier > 1:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed_multiplier = 1
        
        # Update ghost mode timer
        if self.ghost_mode:
            self.ghost_timer -= 1
            if self.ghost_timer <= 0:
                self.ghost_mode = False
                self.color = BLUE
        
        # Update collision rect
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self):
        # Draw with a gradient if in ghost mode
        if self.ghost_mode:
            # Pulsating effect
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            color = (int(100 + 155 * pulse), 0, int(100 + 155 * pulse))
            pygame.draw.rect(window, color, (self.x, self.y, self.width, self.height))
            # Add glow effect
            for i in range(3):
                size = i * 2
                alpha = 100 - i * 30
                s = pygame.Surface((self.width + size*2, self.height + size*2), pygame.SRCALPHA)
                pygame.draw.rect(s, (*color, alpha), (0, 0, self.width + size*2, self.height + size*2))
                window.blit(s, (self.x - size, self.y - size))
        else:
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
            
        # Draw face
        eye_size = 5
        pygame.draw.circle(window, WHITE, (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3)), eye_size)
        pygame.draw.circle(window, BLACK, (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3)), eye_size//2)

class Obstacle:
    def __init__(self, x, height):
        self.width = 30
        self.height = height
        self.x = x
        self.y = WINDOW_HEIGHT - GROUND_HEIGHT - self.height
        self.color = RED
        self.passed = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.particles = []
    
    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x
        
        # Update particles
        for particle in self.particles[:]:
            particle[0] += particle[2]  # x position
            particle[1] += particle[3]  # y position
            particle[4] -= 0.1  # alpha
            if particle[4] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        # Draw particles first (behind the obstacle)
        for particle in self.particles:
            pygame.draw.circle(window, (*self.color, int(particle[4] * 255)), 
                              (int(particle[0]), int(particle[1])), int(particle[4] * 5))
        
        # Draw obstacle with gradient
        for i in range(self.height):
            color_val = max(100, 255 - i)
            pygame.draw.line(window, (color_val, 0, 0), 
                           (self.x, self.y + i), (self.x + self.width, self.y + i))
    
    def collides_with(self, player):
        if player.ghost_mode:
            return False
        return self.rect.colliderect(player.rect)
    
    def add_particles(self, count=5):
        for _ in range(count):
            # [x, y, x_vel, y_vel, alpha]
            self.particles.append([
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                random.uniform(-1, 1),
                random.uniform(-2, 0),
                random.uniform(0.5, 1.0)
            ])

class Coin:
    def __init__(self, x):
        self.radius = 10
        self.x = x
        self.y = random.randint(WINDOW_HEIGHT - GROUND_HEIGHT - 100, WINDOW_HEIGHT - GROUND_HEIGHT - 20)
        self.color = YELLOW
        self.collected = False
        self.angle = 0
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x - self.radius
        self.angle = (self.angle + 5) % 360  # Rotation animation
    
    def draw(self):
        if not self.collected:
            # Draw with a shining effect
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
            
            # Draw inner circle (3D effect)
            inner_radius = int(self.radius * 0.7)
            pygame.draw.circle(window, (255, 215, 0), (int(self.x), int(self.y)), inner_radius)
            
            # Draw shine effect
            shine_pos = (int(self.x + self.radius * 0.3 * math.cos(math.radians(self.angle))), 
                        int(self.y + self.radius * 0.3 * math.sin(math.radians(self.angle))))
            pygame.draw.circle(window, WHITE, shine_pos, 2)
    
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)

class PowerUp:
    def __init__(self, x, power_type=None):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = random.randint(WINDOW_HEIGHT - GROUND_HEIGHT - 100, WINDOW_HEIGHT - GROUND_HEIGHT - 20)
        self.collected = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse = 0
        
        # Randomly choose power type if not specified
        if power_type is None:
            power_type = random.choice(["speed", "ghost"])
        
        self.type = power_type
        
        # Set color based on type
        if self.type == "speed":
            self.color = GREEN
            self.text = "x2"
        elif self.type == "ghost":
            self.color = PURPLE
            self.text = "G"
    
    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x
        self.pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5  # Pulsating effect
    
    def draw(self):
        if not self.collected:
            # Draw with pulsating glow
            glow_size = int(5 * self.pulse)
            for i in range(3):
                size = glow_size + i * 2
                alpha = int(100 * (1 - i/3))
                s = pygame.Surface((self.width + size*2, self.height + size*2), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.width + size*2, self.height + size*2))
                window.blit(s, (self.x - size, self.y - size))
            
            # Draw main power-up
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw text
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text, True, BLACK)
            text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            window.blit(text, text_rect)
    
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)

class UI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Create touch buttons for mobile
        self.jump_button = pygame.Rect(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100, 80, 80)
        self.restart_button = pygame.Rect(20, WINDOW_HEIGHT - 100, 80, 80)
    
    def draw_score(self, score):
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        window.blit(score_text, (10, 10))
    
    def draw_speed(self, multiplier):
        if multiplier > 1:
            speed_text = self.font.render(f"Speed: x{multiplier}", True, GREEN)
            window.blit(speed_text, (10, 50))
    
    def draw_ghost_mode(self, active):
        if active:
            ghost_text = self.font.render("Ghost Mode!", True, PURPLE)
            window.blit(ghost_text, (10, 90))
    
    def draw_game_over(self, score):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {score}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        
        window.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
        window.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
        window.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
    
    def draw_touch_controls(self, game_state):
        # Only draw touch controls on mobile
        if not pygame.key.get_focused():  # Simple check for mobile
            # Jump button
            pygame.draw.circle(window, (200, 200, 200, 150), 
                             (self.jump_button.centerx, self.jump_button.centery), 40)
            jump_text = self.font.render("JUMP", True, BLACK)
            window.blit(jump_text, (self.jump_button.centerx - jump_text.get_width()//2, 
                                  self.jump_button.centery - jump_text.get_height()//2))
            
            # Restart button (only shown on game over)
            if game_state == GAME_OVER:
                pygame.draw.circle(window, (200, 200, 200, 150), 
                                 (self.restart_button.centerx, self.restart_button.centery), 40)
                restart_text = self.font.render("R", True, BLACK)
                window.blit(restart_text, (self.restart_button.centerx - restart_text.get_width()//2, 
                                         self.restart_button.centery - restart_text.get_height()//2))
    
    def check_touch_input(self, pos, game_state, player):
        # Check if jump button was pressed
        if self.jump_button.collidepoint(pos) and game_state == PLAYING:
            player.jump()
            return None
        
        # Check if restart button was pressed
        if self.restart_button.collidepoint(pos) and game_state == GAME_OVER:
            return "restart"
        
        return None

def reset_game():
    player = Player()
    obstacles = []
    coins = []
    power_ups = []
    snowflakes = [Snowflake() for _ in range(MAX_SNOWFLAKES)]
    game_state = PLAYING
    next_obstacle_time = 0
    next_coin_time = 0
    next_power_up_time = 0
    return player, obstacles, coins, power_ups, snowflakes, game_state, next_obstacle_time, next_coin_time, next_power_up_time

def main():
    # Set up for responsive design
    screen_info = pygame.display.Info()
    global WINDOW_WIDTH, WINDOW_HEIGHT
    
    # Check if running on mobile (approximation)
    is_mobile = screen_info.current_w < 1000 and screen_info.current_h < 1000
    if is_mobile:
        # Make window fullscreen on mobile
        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WINDOW_WIDTH = screen_info.current_w
        WINDOW_HEIGHT = screen_info.current_h
    
    player, obstacles, coins, power_ups, snowflakes, game_state, next_obstacle_time, next_coin_time, next_power_up_time = reset_game()
    ui = UI()
    
    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and game_state == PLAYING:
                    player.jump()
                elif event.key == K_r and game_state == GAME_OVER:
                    player, obstacles, coins, power_ups, snowflakes, game_state, next_obstacle_time, next_coin_time, next_power_up_time = reset_game()
            elif event.type == MOUSEBUTTONDOWN:
                # Handle touch input
                action = ui.check_touch_input(event.pos, game_state, player)
                if action == "restart":
                    player, obstacles, coins, power_ups, snowflakes, game_state, next_obstacle_time, next_coin_time, next_power_up_time = reset_game()
        
        # Update game state
        if game_state == PLAYING:
            # Update player
            player.update()
            
            # Update snowflakes
            for snowflake in snowflakes:
                snowflake.update()
            
            # Calculate current speed
            current_speed = SCROLL_SPEED * player.speed_multiplier
            
            # Spawn obstacles
            if pygame.time.get_ticks() > next_obstacle_time:
                height = random.randint(30, 100)
                new_obstacle = Obstacle(WINDOW_WIDTH, height)
                obstacles.append(new_obstacle)
                next_obstacle_time = pygame.time.get_ticks() + random.randint(1000, 2000)
            
            # Spawn coins
            if pygame.time.get_ticks() > next_coin_time:
                coins.append(Coin(WINDOW_WIDTH))
                next_coin_time = pygame.time.get_ticks() + random.randint(1000, 3000)
            
            # Spawn power-ups
            if pygame.time.get_ticks() > next_power_up_time:
                power_type = random.choice(["speed", "ghost"])
                power_ups.append(PowerUp(WINDOW_WIDTH, power_type))
                next_power_up_time = pygame.time.get_ticks() + random.randint(5000, 10000)
            
            # Update obstacles and check collisions
            for obstacle in obstacles[:]:
                obstacle.update(current_speed)
                
                # Check collision
                if obstacle.collides_with(player):
                    game_state = GAME_OVER
                    obstacle.add_particles(10)  # Add particles on collision
                
                # Remove off-screen obstacles
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                    if not obstacle.passed:
                        player.score += 1
                        obstacle.passed = True
            
            # Update coins and check collection
            for coin in coins[:]:
                coin.update(current_speed)
                
                # Check collection
                if not coin.collected and coin.collides_with(player):
                    coin.collected = True
                    player.score += 5
                
                # Remove off-screen or collected coins
                if coin.x + coin.radius < 0 or coin.collected:
                    coins.remove(coin)
            
            # Update power-ups and check collection
            for power_up in power_ups[:]:
                power_up.update(current_speed)
                
                # Check collection
                if not power_up.collected and power_up.collides_with(player):
                    power_up.collected = True
                    
                    if power_up.type == "speed":
                        player.speed_multiplier = 2
                        player.speed_timer = 300  # 5 seconds at 60 FPS
                    elif power_up.type == "ghost":
                        player.ghost_mode = True
                        player.ghost_timer = 300  # 5 seconds at 60 FPS
                        player.color = PURPLE
                
                # Remove off-screen or collected power-ups
                if power_up.x + power_up.width < 0 or power_up.collected:
                    power_ups.remove(power_up)
        
        # Draw everything
        window.fill(BLACK)
        
        # Draw background
        try:
            window.blit(background_img, (0, 0))
        except:
            pass
        
        # Draw snowflakes
        for snowflake in snowflakes:
            snowflake.draw()
        
        # Draw ground
        try:
            window.blit(ground_img, (0, WINDOW_HEIGHT - GROUND_HEIGHT))
        except:
            pygame.draw.rect(window, WHITE, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))
        
        # Draw game objects
        for obstacle in obstacles:
            obstacle.draw()
        for coin in coins:
            coin.draw()
        for power_up in power_ups:
            power_up.draw()
        player.draw()
        
        # Draw UI
        ui.draw_score(player.score)
        ui.draw_speed(player.speed_multiplier)
        ui.draw_ghost_mode(player.ghost_mode)
        ui.draw_touch_controls(game_state)
        
        if game_state == GAME_OVER:
            ui.draw_game_over(player.score)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
