import pygame, random, time
from pygame import Surface

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
        
    def update(self, dt) -> None:
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt
    
    def render(self, screen: Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))


################################################################################################################################################################################

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()
        
        self.previous_time = None
        
        ## Game Constants
        self.GRAVITY_CONSTANT = 1000
        self.PLAYER_VELOCITY = 200
        self.JUMP_CONSTANT = 450
        ##################
        
        self.player = Player(
            self.screen.get_width()/2, 
            self.screen.get_height()/2, 
            self.PLAYER_VELOCITY, 
            self.sprites["player"],
            self.GRAVITY_CONSTANT
        )
    
    def poll_events(self) -> None: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.velocity = -self.JUMP_CONSTANT
                
    
    def update(self) -> None:
        if self.previous_time is None: ##First Iteration
            self.previous_time = time.time()
            
        ##delta_time calc
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now
        
        self.player.update(dt)

    def render(self) -> None:
        self.screen.fill("black")
        
        self.player.render(self.screen)

        pygame.display.update()

    def load_sprites(self) -> dict:
        sprites = {}
        
        sprites["player"] = pygame.transform.scale(pygame.image.load("./gfx/bird.png").convert_alpha(), (50,35))
        
        return sprites

    def run(self) -> None:
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit() 

g = Game()
g.run()