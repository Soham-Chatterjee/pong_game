import pygame, os, sys, random, time
from pygame import draw
from pygame.constants import KEYDOWN
from win32api import GetSystemMetrics

class button():
    def __init__(self, color, x,y,width,height, text_col, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_colour = text_col
    def draw(self,win,outline=None):
        global font
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.Font("Seven Segment.ttf", 45)  
            text = font.render(self.text, 1, self.text_colour)
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

def drawObjects(button):
    button.draw(screen, base_color)

class sprite(pygame.sprite.Sprite):
	def __init__(self,path,x_pos,y_pos):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_pos,y_pos))

class Player(sprite):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed
		self.movement = 0

	def screen_constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen_height:
			self.rect.bottom = screen_height

	def update(self,ball_group):
		self.rect.y += self.movement
		self.screen_constrain()

class Ball(sprite):
	def __init__(self,path,x_pos,y_pos,speed_x,speed_y,paddles):
		super().__init__(path,x_pos,y_pos)
		self.speed_x = speed_x * random.choice((-1,1))
		self.speed_y = speed_y * random.choice((-1,1))
		self.paddles = paddles
		self.active = False
		self.score_time = 0


	def update(self):
		if self.active:
			self.rect.x += self.speed_x
			self.rect.y += self.speed_y
			self.collisions()
		else:
			self.restart_counter()
		
	def collisions(self):
		if self.rect.top <= 0 or self.rect.bottom >= screen_height:
			pygame.mixer.Sound.play(collide_sound)
			self.speed_y *= -1

		if pygame.sprite.spritecollide(self,self.paddles,False):
			pygame.mixer.Sound.play(collide_sound)
			collision_paddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
			if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
				self.speed_x *= -1
			if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
				self.speed_x *= -1
			if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
				self.rect.top = collision_paddle.bottom
				self.speed_y *= -1
			if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
				self.rect.bottom = collision_paddle.top
				self.speed_y *= -1

	def reset_ball(self):
		self.active = False
		self.speed_x *= random.choice((-1,1))
		self.speed_y *= random.choice((-1,1))
		self.score_time = pygame.time.get_ticks()
		self.rect.center = (screen_width/2,screen_height/2)
		pygame.mixer.Sound.play(score_sound)

	def restart_counter(self):
		global frame_count
		current_time = pygame.time.get_ticks()
		countdown_number = 3

		if current_time - self.score_time <= 1000:
			countdown_number = 3
		if 1000 < current_time - self.score_time <= 2000:
			countdown_number = 2
		if 2000 < current_time - self.score_time <= 3000:
			countdown_number = 1
		if current_time - self.score_time >= 3000:
			pygame.mixer.Sound.play(score_sound)
			self.active = True

		time_counter = basic_font.render(str(countdown_number),True,base_color)
		time_counter_rect = time_counter.get_rect(center = (screen_width/2,screen_height/2 + 50))
		pygame.draw.rect(screen,bg_color,time_counter_rect)
		screen.blit(time_counter,time_counter_rect)

class Opponent(sprite):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed

	def update(self,ball_group):
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y:
			self.rect.y -= self.speed
		self.constrain()

	def constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen_height:
			self.rect.bottom = screen_height

class GameManager:
	def __init__(self,ball_group,paddle_group):
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group


	def pause(self):
		loop = 1
		pause_text = basic_font.render(f"Game PAUSED", False, base_color)
		pause_rect = pause_text.get_rect(center=(dimensions[0]/2, 300))
		screen.blit(pause_text, pause_rect)
		pause_text_2 = basic_font.render(f"Press SPACE to resume", False, base_color)
		pause_rect_2 = pause_text_2.get_rect(center=(dimensions[0]/2, 350))
		screen.blit(pause_text_2, pause_rect_2)
		while loop:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						screen.fill((0, 0, 0))
						loop = 0
			pygame.display.update()
			clock.tick(60)

	def run_game(self):

		self.paddle_group.draw(screen)
		self.ball_group.draw(screen)


		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()

	def reset_ball(self):
		if self.ball_group.sprite.rect.right >= screen_width:
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()

	def draw_score(self):
		player_score = basic_font.render(str(self.player_score),True,base_color)
		opponent_score = basic_font.render(str(self.opponent_score),True,base_color)

		player_score_rect = player_score.get_rect(midleft = (screen_width / 2 + 40,20))
		opponent_score_rect = opponent_score.get_rect(midright = (screen_width / 2 - 40, 20))

		screen.blit(player_score,player_score_rect)
		screen.blit(opponent_score,opponent_score_rect)

	


gamestate = 0
prev_game_state = 0
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)
dimensions = (1280, 720)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((screen_width/2-dimensions[0]/2),(screen_height/2-dimensions[1]/2))

pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()


screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Pong Game')


bg_color = pygame.Color('#2F373F')
accent_color = (27,35,43)
base_color = (200, 200, 200)
secon_colour = (60, 60, 60)
basic_font = pygame.font.Font('Seven Segment.ttf', 40)
collide_sound = pygame.mixer.Sound("pong.ogg")
score_sound = pygame.mixer.Sound("score.ogg")
pygame.mixer.music.load("pong.ogg")
middle_strip = pygame.Rect(screen_width/2 - 2,0,4,screen_height)



player = Player('Paddle.png',screen_width - 20,screen_height/2,5)
opponent_ai_easy = Opponent('Paddle.png',20,screen_width/2,7)
opponent_ai_medium = Opponent('Paddle.png',20,screen_width/2,12)
opponent_ai_hard = Opponent('Paddle.png',20,screen_width/2,14)
opponent_human = Player('Paddle.png',20,screen_height/2,5)
paddle_group_ai_easy = pygame.sprite.Group()
paddle_group_ai_easy.add(player)
paddle_group_ai_easy.add(opponent_ai_easy)
paddle_group_ai_medium = pygame.sprite.Group()
paddle_group_ai_medium.add(player)
paddle_group_ai_medium.add(opponent_ai_medium)
paddle_group_ai_hard = pygame.sprite.Group()
paddle_group_ai_hard.add(player)
paddle_group_ai_hard.add(opponent_ai_hard)

paddle_group_human = pygame.sprite.Group()
paddle_group_human.add(player)
paddle_group_human.add(opponent_human)


ball_ai_easy = Ball('Ball.png',screen_width/2,screen_height/2,7,7,paddle_group_ai_easy)
ball_ai_easy_sprite = pygame.sprite.GroupSingle()
ball_ai_easy_sprite.add(ball_ai_easy)
ball_ai_medium = Ball('Ball.png',screen_width/2,screen_height/2,8,8,paddle_group_ai_medium)
ball_ai_medium_sprite = pygame.sprite.GroupSingle()
ball_ai_medium_sprite.add(ball_ai_medium)
ball_ai_hard = Ball('Ball.png',screen_width/2,screen_height/2,9,9,paddle_group_ai_hard)
ball_ai_hard_sprite = pygame.sprite.GroupSingle()
ball_ai_hard_sprite.add(ball_ai_hard)

ball_human = Ball('Ball.png',screen_width/2,screen_height/2,7,7,paddle_group_human)
ball_human_sprite = pygame.sprite.GroupSingle()
ball_human_sprite.add(ball_human)

instructions = button(bg_color, dimensions[0]/2-150, 350, 300, 50, base_color, "Instructions")
sing_player = button(bg_color, dimensions[0]/2-150, 450, 300, 50, base_color, "Single Player")
multiplayer = button(bg_color, dimensions[0]/2-150, 550, 300, 50, base_color, "Multiplayer")
back_button = button(bg_color, dimensions[0]/2-150, 550, 300, 50, base_color, "Back to Menu")
play_again_button = button(bg_color, dimensions[0]/2-150, 450, 300, 50, base_color, "Play Again")
easy_button = button(bg_color, dimensions[0]/2-150, 350, 300, 50, base_color, "Easy")
medium_button = button(bg_color, dimensions[0]/2-150, 450, 300, 50, base_color, "Medium")
hard_button = button(bg_color, dimensions[0]/2-150, 550, 300, 50, base_color, "Hard")

frame_count = 0
frame_rate = 60
start_time = 300
difficulty = ''

game_manager_ai_easy = GameManager(ball_ai_easy_sprite,paddle_group_ai_easy)
game_manager_ai_medium = GameManager(ball_ai_medium_sprite,paddle_group_ai_medium)
game_manager_ai_hard = GameManager(ball_ai_hard_sprite,paddle_group_ai_hard)
game_manager_human = GameManager(ball_human_sprite,paddle_group_human)
sing_player_running = False
multiplayer_running = False
running = True


while running:
	if gamestate == 0:
		prev_game_state = gamestate
		main_string = "Welcome to Pong Game."
		sub_string = "Please select from the below options"
		screen.fill(bg_color)
		drawObjects(instructions)
		drawObjects(sing_player)
		drawObjects(multiplayer)
		main_text = basic_font.render(main_string, True, base_color)
		main_rect = main_text.get_rect(center=(dimensions[0]/2, 100))
		screen.blit(main_text, main_rect)
		sub_text = basic_font.render(sub_string, True, base_color)
		sub_rect = sub_text.get_rect(center=(dimensions[0]/2, 150))
		screen.blit(sub_text, sub_rect)
		pygame.display.update()
		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()

			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if sing_player.isOver(pos):
					gamestate = 2
				elif multiplayer.isOver(pos):
					gamestate = 4
				elif instructions.isOver(pos):
					gamestate = 1
			if event.type == pygame.MOUSEMOTION:
				if sing_player.isOver(pos):
					sing_player.color = base_color
					sing_player.text_colour = bg_color
					multiplayer.color = bg_color
					multiplayer.text_colour = base_color
					instructions.color = bg_color
					instructions.text_colour = base_color
				elif multiplayer.isOver(pos):
					sing_player.color = bg_color
					sing_player.text_colour = base_color
					multiplayer.color = base_color
					multiplayer.text_colour = bg_color
					instructions.color = bg_color
					instructions.text_colour = base_color
				elif instructions.isOver(pos):
					sing_player.color = bg_color
					sing_player.text_colour = base_color
					multiplayer.color = bg_color
					multiplayer.text_colour = base_color
					instructions.color = base_color
					instructions.text_colour = bg_color
				else:
					sing_player.color = bg_color
					sing_player.text_colour = base_color
					multiplayer.color = bg_color
					multiplayer.text_colour = base_color
					instructions.color = bg_color
					instructions.text_colour = base_color

	elif gamestate == 1:
		prev_game_state = gamestate
		head_string = f"Instructions"
		main_string = f"single player:"
		instructions_1 = f"use up and down keys to navigate player paddle"
		main_string_2 = f"multiplayer:"
		instructions_2 = f"use w and s keys to navigate player 1 paddle"
		instructions_3 = f"use up and down keys to navigate player 2 paddle"
		screen.fill(bg_color)
		head_text = basic_font.render(head_string, True, base_color)
		head_rect = head_text.get_rect(center=(dimensions[0]/2, 100))
		screen.blit(head_text, head_rect)
		main_text = basic_font.render(main_string, True, base_color)
		main_rect = main_text.get_rect(center=(dimensions[0]/2, 200))
		screen.blit(main_text, main_rect)
		ins_1_text = basic_font.render(instructions_1, True, base_color)
		ins_1_rect = ins_1_text.get_rect(center=(dimensions[0]/2, 260))
		screen.blit(ins_1_text, ins_1_rect)
		main_2_text = basic_font.render(main_string_2, True, base_color)
		main_2_rect = main_2_text.get_rect(center=(dimensions[0]/2, 360))
		screen.blit(main_2_text, main_2_rect)
		ins_2_text = basic_font.render(instructions_2, True, base_color)
		ins_2_rect = ins_2_text.get_rect(center=(dimensions[0]/2, 420))
		screen.blit(ins_2_text, ins_2_rect)
		ins_3_text = basic_font.render(instructions_3, True, base_color)
		ins_3_rect = ins_3_text.get_rect(center=(dimensions[0]/2, 480))
		screen.blit(ins_3_text, ins_3_rect)
		drawObjects(back_button)
		pygame.display.update()
		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()

			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if back_button.isOver(pos):
					gamestate = 0
			if event.type == pygame.MOUSEMOTION:
				if back_button.isOver(pos):
					back_button.color = base_color
					back_button.text_colour = bg_color
				else:
					back_button.color = bg_color
					back_button.text_colour = base_color
	elif gamestate == 2:
		prev_game_state = gamestate
		main_string = "Single Player Mode"
		sub_string = "Please select difficulty level"
		screen.fill(bg_color)
		drawObjects(easy_button)
		drawObjects(medium_button)
		drawObjects(hard_button)
		main_text = basic_font.render(main_string, True, base_color)
		main_rect = main_text.get_rect(center=(dimensions[0]/2, 100))
		screen.blit(main_text, main_rect)
		sub_text = basic_font.render(sub_string, True, base_color)
		sub_rect = sub_text.get_rect(center=(dimensions[0]/2, 150))
		screen.blit(sub_text, sub_rect)
		pygame.display.update()
		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()

			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if easy_button.isOver(pos):
					difficulty = 'easy'
					gamestate = 3
				elif medium_button.isOver(pos):
					difficulty = 'medium'
					gamestate = 3
				elif hard_button.isOver(pos):
					difficulty = "hard"
					gamestate = 3
			if event.type == pygame.MOUSEMOTION:
				if easy_button.isOver(pos):
					easy_button.color = base_color
					easy_button.text_colour = bg_color
					medium_button.color = bg_color
					medium_button.text_colour = base_color
					hard_button.color = bg_color
					hard_button.text_colour = base_color
				elif medium_button.isOver(pos):
					easy_button.color = bg_color
					easy_button.text_colour = base_color
					medium_button.color = base_color
					medium_button.text_colour = bg_color
					hard_button.color = bg_color
					hard_button.text_colour = base_color
				elif hard_button.isOver(pos):
					easy_button.color = bg_color
					easy_button.text_colour = base_color
					medium_button.color = bg_color
					medium_button.text_colour = base_color
					hard_button.color = base_color
					hard_button.text_colour = bg_color
				else:
					easy_button.color = bg_color
					easy_button.text_colour = base_color
					medium_button.color = bg_color
					medium_button.text_colour = base_color
					hard_button.color = bg_color
					hard_button.text_colour = base_color
	elif gamestate == 3:
		if difficulty == "easy":
			prev_game_state = gamestate
			total_seconds = start_time - (frame_count // frame_rate)
			if total_seconds < 0:
				total_seconds = 0

			minutes = total_seconds // 60

			seconds = total_seconds % 60

			if seconds == 0 and minutes == 0:
				pygame.mixer.Sound.play(score_sound)
				sing_player_running = False
				player.movement = 0
				opponent_ai_easy.movement = 0
				gamestate = 5
				
			output_string = "Time left: {0:02}:{1:02}".format(minutes, seconds)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						player.movement -= player.speed
					if event.key == pygame.K_DOWN:
						player.movement += player.speed
					if event.key == pygame.K_SPACE:
						if ball_ai_easy.active == True:
							game_manager_ai_easy.pause()
					if event.key == pygame.K_RETURN:
						screen.fill((0, 0, 0))
						ball_ai_easy.active = True
						sing_player_running = True
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_UP:
						player.movement += player.speed
					if event.key == pygame.K_DOWN:
						player.movement -= player.speed
				
			screen.fill(bg_color)
			pygame.draw.rect(screen,accent_color,middle_strip)
			pause_text = basic_font.render(f"Single player", False, base_color)
			pause_rect = pause_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(pause_text, pause_rect)
			pause_text_2 = basic_font.render(f"Press ENTER to start", False, base_color)
			pause_rect_2 = pause_text_2.get_rect(center=(dimensions[0]/2, 350))
			screen.blit(pause_text_2, pause_rect_2)
			
			timer_text = basic_font.render(output_string, True, base_color)
			screen.blit(timer_text, (480, 670))
			
			if sing_player_running:
				screen.fill(bg_color)
				player_text = basic_font.render(f"Computer", False, accent_color)
				player_rect = player_text.get_rect(center=(dimensions[0]/4, dimensions[1]/2))
				screen.blit(player_text, player_rect)
				player_text_2 = basic_font.render(f"Player", False, accent_color)
				player_rect_2 = player_text_2.get_rect(center=((dimensions[0]/4)*3, dimensions[1]/2))
				screen.blit(player_text_2, player_rect_2)
				pygame.draw.rect(screen,accent_color,middle_strip)
				timer_text = basic_font.render(output_string, True, base_color)
				screen.blit(timer_text, (480, 670))
				game_manager_ai_easy.run_game()


			if ball_ai_easy.active:
				frame_count +=1
		elif difficulty == "medium":
			prev_game_state = gamestate
			total_seconds = start_time - (frame_count // frame_rate)
			if total_seconds < 0:
				total_seconds = 0

			minutes = total_seconds // 60

			seconds = total_seconds % 60

			if seconds == 0 and minutes == 0:
				pygame.mixer.Sound.play(score_sound)
				sing_player_running = False
				player.movement = 0
				opponent_ai_medium.movement = 0
				gamestate = 5
				
			output_string = "Time left: {0:02}:{1:02}".format(minutes, seconds)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						player.movement -= player.speed
					if event.key == pygame.K_DOWN:
						player.movement += player.speed
					if event.key == pygame.K_SPACE:
						if ball_ai_medium.active == True:
							game_manager_ai_medium.pause()
					if event.key == pygame.K_RETURN:
						screen.fill((0, 0, 0))
						ball_ai_medium.active = True
						sing_player_running = True
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_UP:
						player.movement += player.speed
					if event.key == pygame.K_DOWN:
						player.movement -= player.speed
				
			screen.fill(bg_color)
			pygame.draw.rect(screen,accent_color,middle_strip)
			pause_text = basic_font.render(f"Single player", False, base_color)
			pause_rect = pause_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(pause_text, pause_rect)
			pause_text_2 = basic_font.render(f"Press ENTER to start", False, base_color)
			pause_rect_2 = pause_text_2.get_rect(center=(dimensions[0]/2, 350))
			screen.blit(pause_text_2, pause_rect_2)
			
			timer_text = basic_font.render(output_string, True, base_color)
			screen.blit(timer_text, (480, 670))
			
			if sing_player_running:
				screen.fill(bg_color)
				player_text = basic_font.render(f"Computer", False, accent_color)
				player_rect = player_text.get_rect(center=(dimensions[0]/4, dimensions[1]/2))
				screen.blit(player_text, player_rect)
				player_text_2 = basic_font.render(f"Player", False, accent_color)
				player_rect_2 = player_text_2.get_rect(center=((dimensions[0]/4)*3, dimensions[1]/2))
				screen.blit(player_text_2, player_rect_2)
				pygame.draw.rect(screen,accent_color,middle_strip)
				timer_text = basic_font.render(output_string, True, base_color)
				screen.blit(timer_text, (480, 670))
				game_manager_ai_medium.run_game()


			if ball_ai_medium.active:
				frame_count +=1
		elif difficulty == "hard":
			prev_game_state = gamestate
			total_seconds = start_time - (frame_count // frame_rate)
			if total_seconds < 0:
				total_seconds = 0

			minutes = total_seconds // 60

			seconds = total_seconds % 60

			if seconds == 0 and minutes == 0:
				pygame.mixer.Sound.play(score_sound)
				sing_player_running = False
				player.movement = 0
				opponent_ai_hard.movement = 0
				gamestate = 5
				
			output_string = "Time left: {0:02}:{1:02}".format(minutes, seconds)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						player.movement -= player.speed
					if event.key == pygame.K_DOWN:
						player.movement += player.speed
					if event.key == pygame.K_SPACE:
						if ball_ai_hard.active == True:
							game_manager_ai_hard.pause()
					if event.key == pygame.K_RETURN:
						screen.fill((0, 0, 0))
						ball_ai_hard.active = True
						sing_player_running = True
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_UP:
						player.movement += player.speed
					if event.key == pygame.K_DOWN:
						player.movement -= player.speed
				
			screen.fill(bg_color)
			pygame.draw.rect(screen,accent_color,middle_strip)
			pause_text = basic_font.render(f"Single player", False, base_color)
			pause_rect = pause_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(pause_text, pause_rect)
			pause_text_2 = basic_font.render(f"Press ENTER to start", False, base_color)
			pause_rect_2 = pause_text_2.get_rect(center=(dimensions[0]/2, 350))
			screen.blit(pause_text_2, pause_rect_2)
			
			timer_text = basic_font.render(output_string, True, base_color)
			screen.blit(timer_text, (480, 670))
			
			if sing_player_running:
				screen.fill(bg_color)
				player_text = basic_font.render(f"Computer", False, accent_color)
				player_rect = player_text.get_rect(center=(dimensions[0]/4, dimensions[1]/2))
				screen.blit(player_text, player_rect)
				player_text_2 = basic_font.render(f"Player", False, accent_color)
				player_rect_2 = player_text_2.get_rect(center=((dimensions[0]/4)*3, dimensions[1]/2))
				screen.blit(player_text_2, player_rect_2)
				pygame.draw.rect(screen,accent_color,middle_strip)
				timer_text = basic_font.render(output_string, True, base_color)
				screen.blit(timer_text, (480, 670))
				game_manager_ai_hard.run_game()


			if ball_ai_hard.active:
				frame_count +=1
	elif gamestate == 4:
		prev_game_state = gamestate
		total_seconds = start_time - (frame_count // frame_rate)
		if total_seconds < 0:
			total_seconds = 0

		minutes = total_seconds // 60

		seconds = total_seconds % 60



		if seconds == 0 and minutes == 0:
			pygame.mixer.Sound.play(score_sound)
			multiplayer_running = False
			player.movement = 0
			opponent_human.movement = 0
			gamestate = 5
			
			


		output_string = "Time left: {0:02}:{1:02}".format(minutes, seconds)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					player.movement -= player.speed
				if event.key == pygame.K_DOWN:
					player.movement += player.speed
				if event.key == pygame.K_w:
					opponent_human.movement -= opponent_human.speed
				if event.key == pygame.K_s:
					opponent_human.movement += opponent_human.speed
				if event.key == pygame.K_SPACE:
					if ball_human.active == True:
						game_manager_human.pause()
				if event.key == pygame.K_RETURN:
					screen.fill((0, 0, 0))
					ball_human.active = True
					multiplayer_running = True
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					player.movement += player.speed
				if event.key == pygame.K_DOWN:
					player.movement -= player.speed
				if event.key == pygame.K_w:
					opponent_human.movement += opponent_human.speed
				if event.key == pygame.K_s:
					opponent_human.movement -= opponent_human.speed
			
		screen.fill(bg_color)
		pygame.draw.rect(screen,accent_color,middle_strip)
		pause_text = basic_font.render(f"Multiplayer", False, base_color)
		pause_rect = pause_text.get_rect(center=(dimensions[0]/2, 300))
		screen.blit(pause_text, pause_rect)
		pause_text_2 = basic_font.render(f"Press ENTER to start", False, base_color)
		pause_rect_2 = pause_text_2.get_rect(center=(dimensions[0]/2, 350))
		screen.blit(pause_text_2, pause_rect_2)
		
		timer_text = basic_font.render(output_string, True, base_color)
		screen.blit(timer_text, (480, 670))
		
		if multiplayer_running:
			screen.fill(bg_color)
			player_text = basic_font.render(f"Player 1", False, accent_color)
			player_rect = player_text.get_rect(center=(dimensions[0]/4, dimensions[1]/2))
			screen.blit(player_text, player_rect)
			player_text_2 = basic_font.render(f"Player 2", False, accent_color)
			player_rect_2 = player_text_2.get_rect(center=((dimensions[0]/4)*3, dimensions[1]/2))
			screen.blit(player_text_2, player_rect_2)
			pygame.draw.rect(screen,accent_color,middle_strip)
			timer_text = basic_font.render(output_string, True, base_color)
			screen.blit(timer_text, (480, 670))
			game_manager_human.run_game()


		if ball_human.active:
			frame_count +=1

	elif gamestate == 5:
		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if back_button.isOver(pos):
					frame_count = 0
					frame_rate = 60
					start_time = 10
					game_manager_ai_easy.player_score = 0
					game_manager_ai_easy.opponent_score = 0
					game_manager_ai_medium.player_score = 0
					game_manager_ai_medium.opponent_score = 0
					game_manager_ai_hard.player_score = 0
					game_manager_ai_hard.opponent_score = 0
					game_manager_human.player_score = 0
					game_manager_human.opponent_score = 0
					ball_ai_easy.reset_ball()
					ball_ai_hard.reset_ball()
					ball_ai_medium.reset_ball()
					ball_human.reset_ball()
					difficulty = ''
					gamestate = 0
				elif play_again_button.isOver(pos) and prev_game_state == 3:
					frame_count = 0
					frame_rate = 60
					start_time = 10
					game_manager_ai_easy.player_score = 0
					game_manager_ai_easy.opponent_score = 0
					game_manager_ai_medium.player_score = 0
					game_manager_ai_medium.opponent_score = 0
					game_manager_ai_hard.player_score = 0
					game_manager_ai_hard.opponent_score = 0
					ball_ai_easy.reset_ball()
					ball_ai_hard.reset_ball()
					ball_ai_medium.reset_ball()
					gamestate = 3
				elif play_again_button.isOver(pos) and prev_game_state == 4:
					frame_count = 0
					frame_rate = 60
					start_time = 10
					game_manager_human.player_score = 0
					game_manager_human.opponent_score = 0
					ball_human.reset_ball()
					gamestate = 4
			if event.type == pygame.MOUSEMOTION:
				if back_button.isOver(pos):
					back_button.color = base_color
					back_button.text_colour = bg_color
					play_again_button.color = bg_color
					play_again_button.text_colour = base_color
				elif play_again_button.isOver(pos):
					back_button.color = bg_color
					back_button.text_colour = base_color
					play_again_button.color = base_color
					play_again_button.text_colour = bg_color
				else:
					back_button.color = bg_color
					back_button.text_colour = base_color
					play_again_button.color = bg_color
					play_again_button.text_colour = base_color
		if prev_game_state == 3 and difficulty == "easy":
			head_string = [f"TIME OVER !", "SCORE"]
			score_string = f"Computer : {game_manager_ai_easy.opponent_score} - {game_manager_ai_easy.player_score} : Player"
			if game_manager_ai_easy.player_score == game_manager_ai_easy.opponent_score:
				result_string = f"Its a Draw!"
			elif game_manager_ai_easy.player_score >= game_manager_ai_easy.opponent_score:
				result_string = f"You Win!"
			elif game_manager_ai_easy.player_score <= game_manager_ai_easy.opponent_score:
				result_string = f"Computer wins!"
			screen.fill(bg_color)
			head_text1 = basic_font.render(head_string[0], True, base_color)
			head_text2 = basic_font.render(head_string[1], True, base_color)
			score_text = basic_font.render(score_string, True, base_color)
			result_text = basic_font.render(result_string, True, base_color)
			head_rect1 = head_text1.get_rect(center=(dimensions[0]/2, 100))
			head_rect2 = head_text2.get_rect(center=(dimensions[0]/2, 150))
			result_rect = result_text.get_rect(center=(dimensions[0]/2, dimensions[1]/2))
			score_rect = score_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(head_text1, head_rect1)
			screen.blit(head_text2, head_rect2)
			drawObjects(play_again_button)
			drawObjects(back_button)
			screen.blit(score_text, score_rect)
			screen.blit(result_text, result_rect)
		elif prev_game_state == 3 and difficulty == "medium":
			head_string = [f"TIME OVER !", "SCORE"]
			score_string = f"Computer : {game_manager_ai_medium.opponent_score} - {game_manager_ai_medium.player_score} : Player"
			if game_manager_ai_medium.player_score == game_manager_ai_medium.opponent_score:
				result_string = f"Its a Draw!"
			elif game_manager_ai_medium.player_score >= game_manager_ai_medium.opponent_score:
				result_string = f"You Win!"
			elif game_manager_ai_medium.player_score <= game_manager_ai_medium.opponent_score:
				result_string = f"Computer wins!"
			screen.fill(bg_color)
			head_text1 = basic_font.render(head_string[0], True, base_color)
			head_text2 = basic_font.render(head_string[1], True, base_color)
			score_text = basic_font.render(score_string, True, base_color)
			result_text = basic_font.render(result_string, True, base_color)
			head_rect1 = head_text1.get_rect(center=(dimensions[0]/2, 100))
			head_rect2 = head_text2.get_rect(center=(dimensions[0]/2, 150))
			result_rect = result_text.get_rect(center=(dimensions[0]/2, dimensions[1]/2))
			score_rect = score_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(head_text1, head_rect1)
			screen.blit(head_text2, head_rect2)
			drawObjects(play_again_button)
			drawObjects(back_button)
			screen.blit(score_text, score_rect)
			screen.blit(result_text, result_rect)
		elif prev_game_state == 3 and difficulty == "hard":
			head_string = [f"TIME OVER !", "SCORE"]
			score_string = f"Computer : {game_manager_ai_hard.opponent_score} - {game_manager_ai_hard.player_score} : Player"
			if game_manager_ai_hard.player_score == game_manager_ai_hard.opponent_score:
				result_string = f"Its a Draw!"
			elif game_manager_ai_hard.player_score >= game_manager_ai_hard.opponent_score:
				result_string = f"You Win!"
			elif game_manager_ai_hard.player_score <= game_manager_ai_hard.opponent_score:
				result_string = f"Computer wins!"
			screen.fill(bg_color)
			head_text1 = basic_font.render(head_string[0], True, base_color)
			head_text2 = basic_font.render(head_string[1], True, base_color)
			score_text = basic_font.render(score_string, True, base_color)
			result_text = basic_font.render(result_string, True, base_color)
			head_rect1 = head_text1.get_rect(center=(dimensions[0]/2, 100))
			head_rect2 = head_text2.get_rect(center=(dimensions[0]/2, 150))
			result_rect = result_text.get_rect(center=(dimensions[0]/2, dimensions[1]/2))
			score_rect = score_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(head_text1, head_rect1)
			screen.blit(head_text2, head_rect2)
			drawObjects(play_again_button)
			drawObjects(back_button)
			screen.blit(score_text, score_rect)
			screen.blit(result_text, result_rect)
		elif prev_game_state == 4:
			head_string = [f"TIME OVER !", "SCORE"]
			score_string = f"Player 1 : {game_manager_human.opponent_score} - {game_manager_human.player_score} : Player 2"
			if game_manager_human.player_score == game_manager_human.opponent_score:
				result_string = f"Its a Draw!"
			elif game_manager_human.player_score >= game_manager_human.opponent_score:
				result_string = f"Player 2 Wins!"
			elif game_manager_human.player_score <= game_manager_human.opponent_score:
				result_string = f"Player 1 wins!"
			screen.fill(bg_color)
			head_text1 = basic_font.render(head_string[0], True, base_color)
			head_text2 = basic_font.render(head_string[1], True, base_color)
			score_text = basic_font.render(score_string, True, base_color)
			result_text = basic_font.render(result_string, True, base_color)
			head_rect1 = head_text1.get_rect(center=(dimensions[0]/2, 100))
			head_rect2 = head_text2.get_rect(center=(dimensions[0]/2, 150))
			result_rect = result_text.get_rect(center=(dimensions[0]/2, dimensions[1]/2))
			score_rect = score_text.get_rect(center=(dimensions[0]/2, 300))
			screen.blit(head_text1, head_rect1)
			screen.blit(head_text2, head_rect2)
			drawObjects(play_again_button)
			drawObjects(back_button)
			screen.blit(score_text, score_rect)
			screen.blit(result_text, result_rect)
	pygame.display.flip()
	clock.tick(60)