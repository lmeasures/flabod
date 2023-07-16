import pygame, random, time
from pygame import Surface

################################################################################################################################################################################

class SceneManager:
    def __init__(self) -> None:
        self.scenes = {}
        self.quit = False
        
    def initialize(self, scenes: dict, starting_scene: str) -> None:
        self.scenes = scenes
        self.current_scene = self.scenes[starting_scene]
        
    def set_scene(self, new_scene: str) -> None:
        self.current_scene = self.scenes[new_scene]
        
    def get_scene(self):
        return self.current_scene
    
    def quit_game(self) -> None:
        self.quit = True
        
    def reset_main(self) -> None:
        new_scene = MainScene(self, 
                              self.scenes["main"].screen, 
                              self.scenes["main"].sprites
                            )
        self.scenes["main"] = new_scene
        
    def reset_start(self) -> None:
        new_scene = StartScene(self, 
                                self.scenes["start"].screen, 
                                self.scenes["start"].sprites
                                )
        self.scenes["start"] = new_scene

################################################################################################################################################################################

class Scene:
    def __init__(self,
                 manager: SceneManager,
                 screen: Surface,
                 sprites: dict
                 ) -> None:
        self.manager = manager
        self.screen = screen
        self.sprites = sprites
        
    def update(self) -> None:
        pass
        
    def render(self) -> None:
        pass
        
    def poll_events(self) -> None:
        pass
    
################################################################################################################################################################################

class MainScene(Scene):
    def __init__(self, 
                 manager: SceneManager, 
                 screen: Surface, 
                 sprites: dict
                 ) -> None:
        super().__init__(manager, screen, sprites)
        
        self.previous_time = None
        
        ## Game Constants
        self.GRAVITY_CONSTANT = 1000
        self.PLAYER_VELOCITY = -400 #player starting velocity (minus == upwards)
        self.JUMP_CONSTANT = 450
        self.OBSTACLE_FREQUENCY = 1300
        self.OBSTACLE_VELOCITY = -250
        self.OBSTACLE_GAP = 3
        ##################
        
        self.player = Player(
            self.screen.get_width()/2, 
            self.screen.get_height()/2, 
            self.PLAYER_VELOCITY, 
            self.sprites["player"],
            self.GRAVITY_CONSTANT
        )
        
        self.env = Environment(self.player,
                               self.screen,
                               self.sprites,
                               self.OBSTACLE_FREQUENCY,
                               self.OBSTACLE_VELOCITY,
                               self.OBSTACLE_GAP
                               )
        
        self.score = Score(self.screen.get_width()/2, 50)
        
        self.easy_music_playing = False
        self.easy_music = pygame.mixer.Sound("./sfx/game music start.mp3")
        self.easy_music.set_volume(0.1)
        
        self.intense_music_playing = False
        self.intense_music = pygame.mixer.Sound("./sfx/game music big.mp3")
        self.intense_music.set_volume(0.2)
        
    def play_easy_music(self) -> None:
        self.intense_music.fadeout(1)
        self.intense_music_playing = False
        self.easy_music.play(-1)
        self.easy_music_playing = True
        
    def play_intense_music(self) -> None:
        self.easy_music.fadeout(1)
        self.easy_music_playing = False
        self.intense_music.play(-1)
        self.intense_music_playing = True
        
    def stop_music(self) -> None:
        self.easy_music.fadeout(1)
        self.easy_music_playing = False
        self.intense_music.fadeout(1)
        self.intense_music_playing = False

    def update(self) -> None:
        if self.previous_time is None: ##First Iteration
            self.previous_time = time.time()
            
        ##delta_time calc
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now
        
        self.player.update(dt)
        self.env.update(dt)
            
        if self.env.score_tracker > self.score.score:
            self.score.add_score()
            self.score.update()
            
        if self.env.score_tracker > 0 and self.env.score_tracker <= 60 and self.easy_music_playing == False:
            self.stop_music()
            self.intense_music_playing = False
            self.play_easy_music()
            self.easy_music_playing = True
            
        if self.env.score_tracker > 60 and self.intense_music_playing == False:
            self.stop_music()
            self.easy_music_playing = False
            self.play_intense_music()
            self.intense_music_playing = True

        if self.player_collision() or self.player.y > self.screen.get_height() or self.player.y < -40:
            self.stop_music()
            self.player.play_death()
            self.manager.set_scene("death")
            
    def render(self) -> None:
        self.screen.fill("black")
        
        self.player.render(self.screen)
        self.env.render(self.screen)
        self.score.render(self.screen)
        
        pygame.display.update()
    
    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.velocity -= self.JUMP_CONSTANT
                self.player.play_flap()
                
    def player_collision(self) -> bool:
        for o in self.env.obstacles:
            for b in o.blocks:
                if b.rect.colliderect(self.player.rect):
                    return True
        return False
    
################################################################################################################################################################################

class StartScene(Scene):
    def __init__(self, 
                 manager: SceneManager, 
                 screen: Surface, 
                 sprites: dict
                ) -> None:
        super().__init__(manager, screen, sprites)
        self.font = pygame.font.SysFont("Arial", 36)
        self.text = ".Flabod. Press spac 2b egin"
        self.text_x = 400
        self.text_y = 200
        
        pygame.mixer.music.load("./sfx/menu music.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        
    def update(self) -> None:
        pass
    
    def render(self) -> None:
        self.screen.fill("black")
        
        self.screen.blit(self.font.render(self.text, True, "white"), (self.text_x, self.text_y))
        
        pygame.display.update()
        
    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                self.manager.set_scene("main")
                

################################################################################################################################################################################

class DeathScene(Scene):
    def __init__(self, 
                 manager: SceneManager, 
                 screen: Surface, 
                 sprites: dict
                 ) -> None:
        super().__init__(manager, screen, sprites)
        
        self.font = pygame.font.SysFont("Arial", 36)
        self.text = "ded. R 2 agen"
        self.text_x = 400
        self.text_y = 200
        
    def update(self) -> None:
        pass
    
    def render(self) -> None:
        
        self.screen.blit(self.font.render(self.text, True, "white"), (self.text_x, self.text_y))
        
        pygame.display.update()
        
    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.manager.reset_main()
                self.manager.reset_start()
                self.manager.set_scene("start")

################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################

class Score:
    def __init__(self,
                 x,
                 y,
                ) -> None:
        self.font = pygame.font.SysFont("Calibri", 36, True)
        self.score = 0
        self.text = str(self.score)
        self.x = x
        self.y = y
        
    def add_score(self) -> None:
        self.score += 1
        
    def update(self) -> None:
        self.text = str(self.score)
        
    def render(self, screen: Surface) -> None:
        screen.blit(self.font.render(self.text, True, "white"),(self.x, self.y))

################################################################################################################################################################################

class Entity:
    def __init__(self,
            x: float, 
            y: float, 
            velocity: float,
            sprite: pygame.Surface
        ) -> None:
        self.x = x
        self.y = y
        self.velocity = velocity
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: Surface) -> None:
        pass

################################################################################################################################################################################

class Obstacle(Entity):
    
    class ObstacleBlock(Entity):
        def __init__(self, 
                     x: float,
                     y: float, 
                     velocity: float, 
                     sprite: Surface
                     ) -> None:
            super().__init__(x, y, velocity, sprite)
            self.rect = self.sprite.get_rect()
        
        def update(self, dt) -> None:
            self.x += self.velocity * dt
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
            
        def render(self, screen: Surface) -> None:
            screen.blit(self.sprite, (self.x, self.y))
    
    def __init__(self, 
                 x: float, 
                 y: float, 
                 velocity: float, 
                 screen_height: int,
                 gap_height: int, #number of blocks missing to form a gap
                 gap_location: int, # number of block from the top of the screen that the gap begins at
                 sprite: Surface
                ) -> None:
        super().__init__(x, y, velocity, sprite)
        self.screen_height = screen_height
        self.gap_height = gap_height
        self.gap_location = gap_location
        
        self.BLOCK_SIZE = 48
        
        ## Calc number of blocks required to fill screen-height
        self.num_blocks = round(self.screen_height / self.BLOCK_SIZE)
        
        ## Calc number of blocks required for the gap
        self.gap_range = (self.gap_location, self.gap_location + self.gap_height)
        
        self.blocks = self.create_blocks()
        self.passed = False
        
    def create_blocks(self) -> list[ObstacleBlock]:
        o = []
        current_block = 0
        for i in range(self.num_blocks):
            if i < self.gap_range[0] or i > self.gap_range[1]:
                o.append(Obstacle.ObstacleBlock(self.x, current_block, self.velocity, self.sprite))
            current_block += self.BLOCK_SIZE
        return o
    
    def update(self, dt) -> None:
        self.x += self.velocity * dt
        for b in self.blocks:
            b.update(dt)
            
    def render(self, screen: Surface) -> None:
        for b in self.blocks:
            b.render(screen)
    

################################################################################################################################################################################

class Player(Entity):
    def __init__(self, 
                x: float, 
                y: float, 
                velocity: float, 
                sprite: Surface, 
                gravity_constant: float
            ) -> None:
        super().__init__(x, y, velocity, sprite)
        self.gravity_constant = gravity_constant
        self.rect = pygame.Rect(0,0,35,27)
        
        self.flap_sound = pygame.mixer.Sound("./sfx/flap.mp3")
        self.flap_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound("./sfx/death.mp3")
        self.death_sound.set_volume(0.5)
        
    def update(self, dt) -> None:
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y + 5)
    
    def render(self, screen: Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))
        
    def play_flap(self) -> None:
        self.flap_sound.play()
        
    def play_death(self) -> None:
        self.death_sound.play()


################################################################################################################################################################################


class Environment:
    def __init__(self,
                 player: Player,
                 screen: Surface,
                 sprites: dict,
                 frequency: int,
                 obstacle_velocity: float,
                 obstacle_gap: int 
                ) -> None:
        self.player = player
        self.screen = screen
        self.sprites = sprites
        self.frequency = frequency
        self.obstacle_velocity = obstacle_velocity
        self.obstacle_gap = obstacle_gap

        self.obstacles = [] # All currently active obstacles
        self.obstacle_spawn_point = self.screen.get_width()
        self.new_obstacle_timer = 0
        
        self.score_tracker = 0
        
    def add_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)
        
    def remove_obstacle(self) -> None:
        self.obstacles.pop(0)
        
    def update_obstacles(self, dt) -> None:
        for o in self.obstacles:
            o.update(dt)
            if o.x < -200:
                self.remove_obstacle()
                
            if o.x < self.player.x and not o.passed:
                self.score_tracker += 1
                o.passed = True
                
        if self.new_obstacle_timer > self.frequency: 
            gap = random.randint(2, 10)
            o = Obstacle(self.obstacle_spawn_point, 0, self.obstacle_velocity, self.screen.get_height(), self.obstacle_gap, gap, self.sprites["block"])
            self.add_obstacle(o)
            self.new_obstacle_timer = 0
            
        self.frequency -= 10 * dt
        self.obstacle_velocity -= 1 * dt
        
        self.player.gravity_constant += 10 * dt
        
        self.new_obstacle_timer += 1
        
    def update(self, dt) -> None:
        self.update_obstacles(dt)
        
    def render(self, screen: Surface) -> None:
        for o in self.obstacles: 
            o.render(screen)


################################################################################################################################################################################


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()

        self.scene_manager = SceneManager()
        scenes = {
            "main": MainScene(self.scene_manager, self.screen, self.sprites),
            "start": StartScene(self.scene_manager, self.screen, self.sprites),
            "death": DeathScene(self.scene_manager, self.screen, self.sprites),
            }
        self.scene_manager.initialize(scenes, "start")
        
        
    def poll_events(self) -> None: 
        pass
    
    def update(self) -> None:
        pass
    
    def render(self) -> None:
        pass
    
    def load_sprites(self) -> dict:
        sprites = {}
        
        sprites["player"] = pygame.transform.scale(pygame.image.load("./gfx/bird.png").convert_alpha(), (50, 35))
        sprites["block"] = pygame.transform.scale(pygame.image.load("./gfx/block.png"), (48, 48))
        
        return sprites

    def run(self) -> None:
        while self.running:
            self.scene_manager.current_scene.poll_events()
            self.scene_manager.current_scene.update()
            self.scene_manager.current_scene.render()
            
            if self.scene_manager.quit == True:
                self.running = False
                
        pygame.quit() 

g = Game()
g.run()