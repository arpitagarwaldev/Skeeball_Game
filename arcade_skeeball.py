import pygame
import math
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_BROWN = (101, 67, 33)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 12
        self.color = WHITE
        self.active = False
        self.trail = []
        
    def update(self):
        if self.active:
            # Physics
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.3  # gravity
            self.vx *= 0.99  # friction
            
            # Trail effect
            self.trail.append((int(self.x), int(self.y)))
            if len(self.trail) > 8:
                self.trail.pop(0)
            
            # Boundaries
            if self.x < self.radius or self.x > SCREEN_WIDTH - self.radius:
                self.vx *= -0.7
                self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
            
            if self.y > SCREEN_HEIGHT:
                self.reset()
    
    def draw(self, screen):
        # Draw trail only when active
        if self.active:
            for i, pos in enumerate(self.trail):
                alpha = (i + 1) / len(self.trail)
                trail_color = (int(255 * alpha), int(255 * alpha), int(255 * alpha))
                pygame.draw.circle(screen, trail_color, pos, int(self.radius * alpha * 0.8))
        
        # Always draw ball
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 4), int(self.y - 4)), 4)
    
    def launch(self, power, angle):
        self.active = True
        self.vx = power * math.cos(angle)
        self.vy = power * math.sin(angle)
        self.trail = []
    
    def reset(self):
        self.active = False
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.vx = 0
        self.vy = 0
        self.trail = []

class Hole:
    def __init__(self, x, y, radius, points, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.points = points
        self.color = color
        self.glow = 0
        
    def check_collision(self, ball):
        distance = math.sqrt((ball.x - self.x)**2 + (ball.y - self.y)**2)
        if distance < self.radius and ball.active:
            self.glow = 30
            ball.reset()
            return self.points
        return 0
    
    def draw(self, screen, font):
        # Glow effect
        if self.glow > 0:
            glow_color = (min(255, self.color[0] + self.glow), 
                         min(255, self.color[1] + self.glow), 
                         min(255, self.color[2] + self.glow))
            pygame.draw.circle(screen, glow_color, (self.x, self.y), self.radius + 5)
            self.glow -= 1
        
        # Hole
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius + 3)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
        # Points text
        text = font.render(str(self.points), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class SkeeballGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎯 Arcade Skeeball Champions 🏆")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game objects
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.holes = [
            Hole(500, 150, 30, 100, GOLD),      # Center - highest points
            Hole(400, 200, 25, 50, RED),        # Left
            Hole(600, 200, 25, 50, RED),        # Right
            Hole(350, 280, 20, 25, BLUE),       # Far left
            Hole(650, 280, 20, 25, BLUE),       # Far right
            Hole(300, 350, 18, 10, GREEN),      # Outer left
            Hole(700, 350, 18, 10, GREEN),      # Outer right
        ]
        
        # Game state
        self.score = 0
        self.balls_left = 10
        self.power = 0
        self.angle = -math.pi/2
        self.charging = False
        self.game_over = False
        self.player_name = ""
        self.input_active = False
        self.high_scores = self.load_high_scores()
        
    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f, indent=2)
    
    def add_high_score(self, name, score):
        self.high_scores.append({
            'name': name,
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        self.save_high_scores()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.player_name.strip():
                            self.add_high_score(self.player_name.strip(), self.score)
                            self.reset_game()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode
                
                elif self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.input_active = True
                        self.player_name = ""
                    elif event.key == pygame.K_r:
                        self.reset_game()
                
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN and not self.ball.active and not self.game_over:
                if self.balls_left > 0:
                    self.charging = True
            
            if event.type == pygame.MOUSEBUTTONUP and self.charging:
                if self.balls_left > 0:
                    self.ball.launch(self.power, self.angle)
                    self.balls_left -= 1
                    self.power = 0
                    self.charging = False
    
    def update(self):
        if not self.game_over:
            # Update ball
            self.ball.update()
            
            # Check collisions
            for hole in self.holes:
                points = hole.check_collision(self.ball)
                if points > 0:
                    self.score += points
            
            # Update power and angle when charging
            if self.charging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - self.ball.x
                dy = mouse_y - self.ball.y
                self.angle = math.atan2(dy, dx)
                distance = math.sqrt(dx*dx + dy*dy)
                self.power = min(20, distance / 10)
            
            # Check game over
            if self.balls_left == 0 and not self.ball.active:
                self.game_over = True
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(20 + (60 - 20) * color_ratio)
            g = int(30 + (80 - 30) * color_ratio)
            b = int(60 + (120 - 60) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Skeeball lane
        pygame.draw.rect(self.screen, DARK_BROWN, (200, 400, 600, 300))
        pygame.draw.rect(self.screen, BROWN, (210, 410, 580, 280))
        
        # Lane lines
        for i in range(5):
            x = 250 + i * 125
            pygame.draw.line(self.screen, DARK_BROWN, (x, 410), (x, 690), 2)
    
    def draw_ui(self):
        # Score
        score_text = self.font_large.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Balls left
        balls_text = self.font_medium.render(f"Balls: {self.balls_left}", True, WHITE)
        self.screen.blit(balls_text, (20, 70))
        
        # Power meter
        if self.charging:
            meter_width = 200
            meter_height = 20
            meter_x = SCREEN_WIDTH - meter_width - 20
            meter_y = 20
            
            pygame.draw.rect(self.screen, GRAY, (meter_x, meter_y, meter_width, meter_height))
            power_width = int((self.power / 20) * meter_width)
            color = GREEN if self.power < 15 else ORANGE if self.power < 18 else RED
            pygame.draw.rect(self.screen, color, (meter_x, meter_y, power_width, meter_height))
            
            power_text = self.font_small.render("POWER", True, WHITE)
            self.screen.blit(power_text, (meter_x, meter_y - 25))
        
        # Instructions
        if not self.ball.active and not self.game_over and self.balls_left > 0:
            inst_text = self.font_small.render("Click and drag to aim, release to shoot!", True, WHITE)
            text_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
            self.screen.blit(inst_text, text_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.input_active:
            # Name input
            title = self.font_large.render("Enter Your Name:", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(title, title_rect)
            
            name_text = self.font_medium.render(self.player_name + "_", True, GOLD)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, 250))
            self.screen.blit(name_text, name_rect)
            
            inst = self.font_small.render("Press ENTER to save score", True, WHITE)
            inst_rect = inst.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(inst, inst_rect)
        else:
            # Game over screen
            title = self.font_large.render("🎯 GAME OVER! 🎯", True, GOLD)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(title, title_rect)
            
            final_score = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(final_score, score_rect)
            
            # High scores
            hs_title = self.font_medium.render("🏆 HIGH SCORES 🏆", True, GOLD)
            hs_rect = hs_title.get_rect(center=(SCREEN_WIDTH//2, 280))
            self.screen.blit(hs_title, hs_rect)
            
            for i, score_data in enumerate(self.high_scores[:5]):
                rank_text = f"{i+1}. {score_data['name']} - {score_data['score']}"
                color = GOLD if i == 0 else WHITE
                text = self.font_small.render(rank_text, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 320 + i * 30))
                self.screen.blit(text, text_rect)
            
            # Instructions
            space_text = self.font_small.render("Press SPACE to save your score", True, GREEN)
            space_rect = space_text.get_rect(center=(SCREEN_WIDTH//2, 550))
            self.screen.blit(space_text, space_rect)
            
            restart_text = self.font_small.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 580))
            self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.score = 0
        self.balls_left = 10
        self.game_over = False
        self.input_active = False
        self.player_name = ""
        self.ball.reset()
        self.charging = False
        self.power = 0
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            
            # Draw everything
            self.draw_background()
            
            # Draw holes
            for hole in self.holes:
                hole.draw(self.screen, self.font_small)
            
            # Draw ball
            self.ball.draw(self.screen)
            
            # Draw trajectory line when aiming
            if self.charging and not self.ball.active:
                end_x = self.ball.x + math.cos(self.angle) * self.power * 10
                end_y = self.ball.y + math.sin(self.angle) * self.power * 10
                pygame.draw.line(self.screen, WHITE, (self.ball.x, self.ball.y), (end_x, end_y), 2)
            
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    try:
        game = SkeeballGame()
        print("🎯 Starting Arcade Skeeball Champions...")
        print("Game window should appear shortly!")
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        print("Try the web version by opening index.html in your browser!")