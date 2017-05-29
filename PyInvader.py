#System
import sys
sys.path.append("modules") #For PyGame
import thread
import time
import random

#PyGame
import pygame
from pygame.locals import *
from pygame.constants import *

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class Video:
    SCREEN = None
    FULLSCREEN = None
    def SetDisplay(self, Width, Height, FullScreen):
        #Set screen size
        if FullScreen == False:
            self.SCREEN = pygame.display.set_mode((Width, Height), DOUBLEBUF)
            self.FULLSCREEN = False
        else:
            self.SCREEN = pygame.display.set_mode((Width, Height), FULLSCREEN | DOUBLEBUF)
            self.FULLSCREEN = True

        #Set Window caption
        pygame.display.set_caption("PyInvader")

        #Fill screen with background color
        self.SCREEN.fill((0,0,0))

        #Update screen display
        pygame.display.flip()

    def getFullscreen(self):
        #Return FULLSCREEN value
        return self.FULLSCREEN

class FPS:
    FRAMES_PER_SEC = None
    CLOCK = None
    def __init__(self):
        #Setup Variables
        self.FRAMES_PER_SEC = 30
        self.CLOCK = pygame.time.Clock()

    def Tick(self):
        #Tick PyGame Clock for FPS regulation
        return self.CLOCK.tick(self.FRAMES_PER_SEC)

class AlienType:
    #Alien Type 0 (Blank)
    def Type0(self):
        return -1

    #Alien Type 1
    def Type1(self):
        return 0

    #Alien Type 2
    def Type2(self):
        return 1

    #Alien Type 3
    def Type3(self):
        return 2

    #Alien Type Mother Ship - (The red mothership)
    def MotherShip(self):
        return 3

    #Setup Static Methods
    Type0 = Callable(Type0)
    Type1 = Callable(Type1)
    Type2 = Callable(Type2)
    Type3 = Callable(Type3)
    MotherShip = Callable(MotherShip)

class EnemyManagement:
    #Typical formation in the arcade version was 11 across and 5 down
    #Top row being of Type1, second and third rows being of Type2, and
    #the last two rows being of Type3
    NUM_ACROSS = 11
    NUM_ROWS = 5

    ENEMY_LIST = []
    #32 representing the size of sprite PLUS the buffer zone between each sprite
    tmpSurface = pygame.Surface(((NUM_ACROSS*45),(NUM_ROWS*45)))
    tmpSurface.set_colorkey((0,0,0))
    tmpSurface.fill(tmpSurface.get_colorkey())

    #For movement acorss and down screen
    MOVEMENT = "INCREASE"
    MoveX = 0
    MoveY = 0

##################################
    class EnemyAlien:
        HEALTH = None
        TYPE = None
        SPRITE = None
        FRAME = None
        XPOS = None
        YPOS = None
        STOP_THREADS = None

        FIRE_SPRITE = None
        FIRE_XPOS = None
        FIRE_YPOS = None
        FIRE_SPEED = None
        FIRE_DISPLAY = None

        def __init__(self, Health, Type):
            #Setup Variables
            self.HEALTH = Health
            self.TYPE = Type
            self.SPRITE = []
            self.FRAME = 0
            self.STOP_THREADS = False

            if self.TYPE == AlienType.Type0:
                tmpSurface = pygame.Surface((27,20))
                tmpSurface.fill((0,0,0))
                self.SPRITE.append(tmpSurface)
                self.SPRITE.append(tmpSurface)

            elif self.TYPE == AlienType.Type1:
                self.SPRITE.append(pygame.image.load("data/images/Alien1a.png"))
                self.SPRITE.append(pygame.image.load("data/images/Alien1b.png"))

            elif self.TYPE == AlienType.Type2:
                self.SPRITE.append(pygame.image.load("data/images/Alien2a.png"))
                self.SPRITE.append(pygame.image.load("data/images/Alien2b.png"))

            elif self.TYPE == AlienType.Type3:
                self.SPRITE.append(pygame.image.load("data/images/Alien3a.png"))
                self.SPRITE.append(pygame.image.load("data/images/Alien3b.png"))

            elif self.TYPE == AlienType.MotherShip:
                self.SPRITE.append(pygame.image.load("data/images/Mothership.png"))
                self.SPRITE.append(pygame.image.load("data/images/Mothership.png"))
            else:
                self.SPRITE = None
                print "[Error]: Enemy Alien type was not set correctly!"
                sys.exit(0)
            self.XPOS = 0
            self.YPOS = 0

            self.FIRE_SPRITE = pygame.image.load("data/images/Missile_Alien.png")
            self.FIRE_XPOS = self.XPOS
            self.FIRE_YPOS = self.YPOS
            self.FIRE_SPEED = (3 + DIFFICULTY) * 2
            self.FIRE_DISPLAY = False

        def Fire(self):
            #Check if we can fire - Based on Type
            if self.TYPE != AlienType.Type0:
                #Make sure we are not already firing
                if self.FIRE_DISPLAY == False:
                    #Update Vars
                    self.FIRE_XPOS = self.XPOS
                    self.FIRE_YPOS = self.YPOS

                    #Set to true so that our missile will render
                    self.FIRE_DISPLAY = True


        def Animate_Thread(self): #Meant to be called in a new thread
            #Update Animation Frame
            while self.STOP_THREADS == False:
                if self.FRAME == 0:
                    self.FRAME = 1
                elif self.FRAME == 1:
                    self.FRAME = 0

                #Sleep
                time.sleep(0.3)

        def Render(self):
            #Blit Alien to tmpSurface
            EnemyManagement.tmpSurface.blit(self.SPRITE[self.FRAME], (self.XPOS, self.YPOS))

        def getHP(self):
            #Return Alien HP
            return self.HEALTH

        def getType(self):
            #Return Alien type
            return self.TYPE

        def getX(self):
            #Return Alien xpos
            return self.XPOS

        def getY(self):
            #Return Alien ypos
            return self.YPOS

        def setX(self, xpos):
            #Set XPos
            self.XPOS = xpos

        def setY(self, ypos):
            #Set YPos
            self.YPOS = ypos

        def setType(self, Type):
            #Set AlienType
            self.TYPE = Type

        def stopThreads(self):
            #Set Flag Variable to False
            self.STOP_THREADS = False
##################################


    def __init__(self):
        #Setup Varaibles
        self.ENEMY_LIST = []

    def Generate(self):
        #clear up the last round
        self.ENEMY_LIST = []
        self.MoveX = 0
        self.MoveY = 0

        #Generate Enemy list based on arcade version
        for i in range(0, self.NUM_ROWS):
            #Gererate the current row (going across)
            for i2 in range(0, self.NUM_ACROSS):
                #What EnemyType should we use?
                if i == 0:
                    tmpEnemy = self.EnemyAlien(100, AlienType.Type1)
                    self.ENEMY_LIST.append(tmpEnemy)
                    tmpEnemy = None #Garbage Collection
                elif i == 1 or i == 2:
                    tmpEnemy = self.EnemyAlien(100, AlienType.Type2)
                    self.ENEMY_LIST.append(tmpEnemy)
                    tmpEnemy = None #Garbage Collection
                elif i == 3 or i == 4:
                    tmpEnemy = self.EnemyAlien(100, AlienType.Type3)
                    self.ENEMY_LIST.append(tmpEnemy)
                    tmpEnemy = None #Garbage Collection

        #Go through and start the Animation thread for each element in ENEMY_LIST
        #Also Setup additional stuff
        for i in range(0, len(self.ENEMY_LIST)):
            #Start Animation Thread
            thread.start_new_thread(self.ENEMY_LIST[i].Animate_Thread, ())

    def Render(self):
        #Keep track of the current row and column
        currentRow = 0
        currentAcross = 0

        #Loop through each element in the ENEMY_LIST array, and render according
        for i in range(0, len(self.ENEMY_LIST)):
            #Set the x,y pos for the Enemy Alien
            self.ENEMY_LIST[i].setX((currentAcross * (27+13)))
            self.ENEMY_LIST[i].setY((currentRow * (20+13)))


            #Render the Enemy Alien
            self.ENEMY_LIST[i].Render()

            #Update Enemy X,Y pos in relationship to their movement acorss screen
            self.ENEMY_LIST[i].setX(self.ENEMY_LIST[i].getX() + self.MoveX)
            self.ENEMY_LIST[i].setY(self.ENEMY_LIST[i].getY() + self.MoveY)

            #Make sure we are within our rendering bounds
            if currentAcross < self.NUM_ACROSS:
                currentAcross += 1 #Update current column

                #Check if we are still within bounds
                if currentAcross == self.NUM_ACROSS:
                    #Reset column count
                    currentAcross = 0

                    #Move on to the next row
                    currentRow += 1

            #Check if we need to render missiles
            if self.ENEMY_LIST[i].FIRE_DISPLAY == True:
                #Render
                pygame.display.get_surface().blit(self.ENEMY_LIST[i].FIRE_SPRITE, (self.ENEMY_LIST[i].FIRE_XPOS, self.ENEMY_LIST[i].FIRE_YPOS))

                #Update Missile Data (Keep missile moving down; Collision with player is checked elsewhere)
                if self.ENEMY_LIST[i].FIRE_YPOS < 450:
                    self.ENEMY_LIST[i].FIRE_YPOS += self.ENEMY_LIST[i].FIRE_SPEED
                else:
                    self.ENEMY_LIST[i].FIRE_DISPLAY = False

        #Blit tmpSurface to screen
        pygame.display.get_surface().blit(self.tmpSurface, (self.MoveX, self.MoveY))

        #Move Enemies acoross / down screen
        if self.MOVEMENT == "INCREASE":
            if self.MoveX < 350:
                self.MoveX += DIFFICULTY
            else:
                self.MoveY += (20+13)
                self.MOVEMENT = "DECREASE"

        if self.MOVEMENT == "DECREASE":
            if self.MoveX > 0:
                self.MoveX -=  DIFFICULTY
            else:
                self.MoveY += (20+13)
                self.MOVEMENT = "INCREASE"



    def Kill(self, ID):
        #self.ENEMY_LIST[ID] = pygame.Surface((32,32))
        #self.ENEMY_LIST.remove(self.ENEMY_LIST[ID])
        self.ENEMY_LIST[ID] = self.EnemyAlien(0, AlienType.Type0)

    def isEmpty(self):
        for alien in self.ENEMY_LIST:
            if alien.TYPE != AlienType.Type0:
                return False

        return True

class Player:
    SPRITE = None
    HEALTH = None
    XPOS = None
    YPOS = None
    MOVE_SPEED = None
    LIFE = None
    SCORE = None

    FIRE_SPRITE = None
    FIRE_DISPLAY = None
    FIRE_XPOS = None
    FIRE_YPOS = None
    FIRE_SPEED = None

    def __init__(self):
        #Setup Variables
        self.SPRITE = pygame.image.load("data/images/Player.png")
        self.HEALTH = 100
        self.XPOS = 400
        self.YPOS = 450
        self.MOVE_SPEED = 8
        self.LIFE = 3 #3 Lives
        self.SCORE = 0

        self.FIRE_SPRITE = pygame.image.load("data/images/Missile_Player.png")
        self.FIRE_DISPLAY = False
        self.FIRE_XPOS = self.XPOS + (self.SPRITE.get_width() / 2)
        self.FIRE_YPOS = self.YPOS
        self.FIRE_SPEED = (3 + DIFFICULTY) * 3

    def MoveRight(self):
        #Move player to the right based upon speed
        self.XPOS += self.MOVE_SPEED

    def MoveLeft(self):
        #Move player to the left based upon speed
        self.XPOS -= self.MOVE_SPEED

    def Move(self, amount):
        self.XPOS += int(round(amount * self.MOVE_SPEED,0))

    def Fire_Thread(self):
        #while within screen AND no collsion has happened:
        #  display bullet
        #  increase x cord until off screen
        #hide bullet
        #reset bullet vars

        #FPS
        fps = FPS()

        while (self.FIRE_DISPLAY == True) and (-1*(self.FIRE_YPOS) < 0):
            #Update missile location based upon speed
            self.FIRE_YPOS -= self.FIRE_SPEED

            #Sleep -- Replace with FPS tick
            #time.sleep(0.01)
            fps.Tick()

        #Update variables to defaults
        self.FIRE_DISPLAY = False
        self.FIRE_XPOS = self.XPOS + (self.SPRITE.get_width() / 2)
        self.FIRE_YPOS = self.YPOS

    def Fire(self):
        #Make sure another thread isn't running for fireing
        if self.FIRE_DISPLAY != True:
            #Update Missile X,Y before starting thread
            self.FIRE_XPOS = self.XPOS+ (self.SPRITE.get_width() / 2)
            self.FIRE_YPOS = self.YPOS

            self.FIRE_DISPLAY = True
            SoundChannel.play(SoundPlayerFire)

            #Start Missile Management Thread
            thread.start_new_thread(self.Fire_Thread, ())

    def Render(self):
        #Render Player, and Missile(If Fireing)
        pygame.display.get_surface().blit(self.SPRITE, (self.XPOS, self.YPOS))
        if self.FIRE_DISPLAY == True:
            pygame.display.get_surface().blit(self.FIRE_SPRITE, (self.FIRE_XPOS, self.FIRE_YPOS))



#Setup Variables
START_GAME = False
GAME_OVER = False
DIFFICULTY = 1

#Setup Classes
video = Video()
fps = FPS()
enemy_man = EnemyManagement()
player = Player()

#Init Pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

#Hide Mouse
pygame.mouse.set_visible(0)

#Enable Keyinput repeat
pygame.key.set_repeat(10,10)

#Initialise the Joysticks
pygame.joystick.init()

#Create Joystick to listen to and initialise it
joystick = pygame.joystick.Joystick(0)
joystick.init()

#Create two channels for music and sound
SoundChannel = pygame.mixer.Channel(0)
pygame.mixer.music.load("data/sounds/music.ogg")

SoundAlienDeath = pygame.mixer.Sound("data/sounds/hit.wav")
SoundPlayerFire = pygame.mixer.Sound("data/sounds/fire.wav")
SoundPlayerHit = pygame.mixer.Sound("data/sounds/explosion.wav")

#Setup Video
video.SetDisplay(800, 600, False)

#Generate Enemy List
enemy_man.Generate()

#Setup TTF Stuff
Player_Info_Font = pygame.font.Font("data/fonts/VeraMoBd.ttf", 14)
GameOver_Font = pygame.font.Font("data/fonts/VeraMoBd.ttf", 20)

#Decides what enemy alien's can fire, and when
def EnemyFire_Monitor():
    #Enemy Fireing Loop - Decide what enemy aliens should fire
    Old_Rnd = 0
    Enemy_Can_Fire = [] #Keeps Track of what Enemy Aliens can fire (By ID)
    while True:
        for i in range(1, len(enemy_man.ENEMY_LIST)):
            try:
                #If the alien right below ENEMY_LIST[i] is Type0, then fire
                if enemy_man.ENEMY_LIST[i + enemy_man.NUM_ACROSS].TYPE == AlienType.Type0:
                    #enemy_man.ENEMY_LIST[i].Fire()
                    Enemy_Can_Fire.append(int(i))
            except: #If index is out of bounds, the bottom row should fire
                #enemy_man.ENEMY_LIST[i].Fire()
                Enemy_Can_Fire.append(int(i))

            #Randomly decide what alien fires
            try:
                #Generate random number based on what enemies can fire
                Rnd = random.randrange(int(min(Enemy_Can_Fire)), int(max(Enemy_Can_Fire)))

                #Prevent the same enemy from being chosen to fire
                if Rnd != Old_Rnd:
                    #Update Old_Rnd placeholder
                    Old_Rnd = Rnd

                    #Have the enemy that was chosen fire
                    enemy_man.ENEMY_LIST[Rnd].Fire()

                    #Break from loop
                    break
                else:
                    #Regenerate number baved on what enemies can fire
                    Rnd = random.randrange(int(min(Enemy_Can_Fire)), int(max(Enemy_Can_Fire)))
            except:
                #If exception is thrown, do nothing
                None

        #Clear Enemy_Can_Fire List
        Enemy_Can_Fire = None
        Enemy_Can_Fire = []

        time.sleep(1/float(DIFFICULTY * 2))

#Start the Enemy Fire Monitoring Thread
thread.start_new_thread(EnemyFire_Monitor, ())

#Game Loop
Loop_Count = 0 #Keep track of how many times we have looped
Loop_Count_GameOver = 0 #Keep track of many times the game over loop has looped
while 1:
    ##################################
    #GAME STUFF
    if START_GAME == True and GAME_OVER == False:
        #Check Player Life Count
        if player.LIFE <= 0:
            #Since the player has no more lives, the game is over
            pygame.mixer.music.stop()
            GAME_OVER = True

        #FPS
        fps.Tick()

        #Movement

        player.Move(joystick.get_axis(0))

        #Events
        for event in pygame.event.get():
            #Catch key and Joystickevents - Basically the controls
            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == K_RIGHT:
                    player.Move(1)
                if event.key == K_LEFT:
                    player.Move(-1)
                if event.key == K_SPACE:
                    player.Fire()
                if event.key == K_f:
                    if video.getFullscreen() == False:
                        video.SetDisplay(800, 600, True)
                    else:
                        video.SetDisplay(800, 600, False)

                # CAN I HAZ CHEATS?
                # if event.key == K_F1:
                #     player.LIFE += 1
                # if event.key == K_F2:
                #     player.SCORE += 500
                # if event.key == K_F3:
                #     player.FIRE_SPEED += 2

            if event.type == JOYBUTTONDOWN:

                if event.button == 2:
                    player.Fire()
                if event.button == 3:
                    pygame.quit()
                    sys.exit(0)
                if event.button == 1:
                    if video.getFullscreen() == False:
                        video.SetDisplay(800, 600, True)
                    else:
                        video.SetDisplay(800, 600, False)

        #spawn new wave
        if enemy_man.isEmpty():
            enemy_man.Generate()
            #update difficulty
            DIFFICULTY += 1

            player.FIRE_SPEED += 2


        #Collision Check - Player Missile Hitting Enemy Alien
        for i in range(0, len(enemy_man.ENEMY_LIST)):
            #Dont Check Type0 Enemy Types
            if enemy_man.ENEMY_LIST[i].getType() != AlienType.Type0:
                if(player.FIRE_SPRITE.get_rect( center=(player.FIRE_XPOS, player.FIRE_YPOS) ).colliderect\
                   (enemy_man.ENEMY_LIST[i].SPRITE[enemy_man.ENEMY_LIST[i].FRAME].get_rect\
                    ( center=(enemy_man.ENEMY_LIST[i].getX(), enemy_man.ENEMY_LIST[i].getY()) ))) == True:

                    #print "Collision[", i, "]"
                    player.FIRE_DISPLAY = False #Hide Player Missile

                    SoundChannel.play(SoundAlienDeath)

                    #Update player's score accordingly
                    if enemy_man.ENEMY_LIST[i].getType() == AlienType.Type1:
                        player.SCORE += 50
                    elif enemy_man.ENEMY_LIST[i].getType() == AlienType.Type2:
                        player.SCORE += 40
                    elif enemy_man.ENEMY_LIST[i].getType() == AlienType.Type3:
                        #Since there are two rows of Type3, there are two
                        #score possibilites
                        index = random.randrange(0,10)
                        if index <= 5:
                            player.SCORE += 20
                        else:
                            player.SCORE += 30
                    elif enemy_man.ENEMY_LIST[i].getType() == AlienType.MotherShip:
                        player.SCORE += 250

                    enemy_man.Kill(i) #"Kill" Enemy Alien that was hit

                    #Break from collision check loop
                    break

        #Collision Check - Enemy Missile Hitting Player
        for i in range(0, len(enemy_man.ENEMY_LIST)):
            if(enemy_man.ENEMY_LIST[i].FIRE_SPRITE.get_rect(center=(enemy_man.ENEMY_LIST[i].FIRE_XPOS, enemy_man.ENEMY_LIST[i].FIRE_YPOS) ).colliderect\
                (player.SPRITE.get_rect(center=(player.XPOS, player.YPOS)))) == True:

                    if enemy_man.ENEMY_LIST[i].FIRE_DISPLAY == True:
                        #Remove a life from player
                        player.LIFE -= 1

                        SoundChannel.play(SoundPlayerHit)

                    #Update Enemy Missile Variables
                    enemy_man.ENEMY_LIST[i].FIRE_DISPLAY = False
                    enemy_man.ENEMY_LIST[i].FIRE_XPOS = 0
                    enemy_man.ENEMY_LIST[i].FIRE_YPOS = 0

                    #Break from collisioin check loop
                    break

        #Clear screen before rendering
        video.SCREEN.fill((0,0,0))

        #Rendering (Blitting)
        enemy_man.Render()
        player.Render()

        #Render Player Information
        Score_Str = "Score: " + str(player.SCORE)
        Score_Surface = Player_Info_Font.render(str(Score_Str), False, (255,255,255))
        Life_Str = "Lives: x" + str(player.LIFE)
        Life_Surface = Player_Info_Font.render(str(Life_Str), False, (255,255,255))
        for i in range(0, int(player.LIFE)):
            #Blit Images to represent number of current lifes
            pygame.display.get_surface().blit(player.SPRITE, (90 + (i*(player.SPRITE.get_width()+10)), 548))

        pygame.draw.line(pygame.display.get_surface(), (0,255,0), (0, 500), (900, 500), 2)
        pygame.display.get_surface().blit(Score_Surface, (10, 500))
        pygame.display.get_surface().blit(Life_Surface, (10, 550))

        #Update screen
        pygame.display.flip()
    ##################################

    #MENU STUFF
    elif START_GAME == False:
        if Loop_Count < 1:
            Menu_Logo = pygame.image.load("data/images/Logo.png")
            Start_Game_Text = Player_Info_Font.render("Press Enter To Begin", False, (0,255,0))
            Exit_Game_Text = Player_Info_Font.render("Press Escape To Exit", False, (255,0,0))
            Control_Text = pygame.image.load("data/images/Controls.png")
            video.SetDisplay(420, 400, False)

            #FPS
            fps.Tick()

        #Events
        for event in pygame.event.get():
            #Keydown
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == K_RETURN:
                    START_GAME = True
                    pygame.mixer.music.play(-1)
                    video.SetDisplay(800, 600, video.getFullscreen())
                    break
                if event.key == K_BACKSLASH:
                    if video.getFullscreen() == False:
                        video.SetDisplay(420, 400, True)
                        Loop_Count = 0 #Re-Load data for menu, and render
                    else:
                        video.SetDisplay(420, 400, False)
                        Loop_Count = 0 #Re-Load data for menu, and render

            if event.type == JOYBUTTONDOWN:

                if event.button == 2:
                    START_GAME = True
                    pygame.mixer.music.play(-1)
                    video.SetDisplay(800, 600, video.getFullscreen())
                    break

                if event.button == 3:
                    pygame.quit()
                    sys.exit(0)
                if event.button == 1:
                    if video.getFullscreen() == False:
                        video.SetDisplay(800, 600, True)
                    else:
                        video.SetDisplay(800, 600, False)



        pygame.display.get_surface().blit(Menu_Logo, (0,0))
        pygame.display.get_surface().blit(Start_Game_Text, (10,250))
        pygame.display.get_surface().blit(Exit_Game_Text, (10,300))
        pygame.display.get_surface().blit(Control_Text, (190,255))
        if Loop_Count < 1:
            #Update screen
            pygame.display.flip()

    #GAME OVER STUFF
    elif GAME_OVER == True:
        if Loop_Count_GameOver < 1:
            #GameOver_Text = GameOver_Font.render("GAME OVER!", False, (255,0,0))
            GameOver_Image = pygame.image.load("data/images/GameOver.png")
            Score_Str = str(player.SCORE)
            Score_Surface = Player_Info_Font.render(str(Score_Str), False, (255,255,255))
            Life_Str = str(player.LIFE)
            Life_Surface = Player_Info_Font.render(str(Life_Str), False, (255,255,255))

        #FPS
        fps.Tick()

        #Events
        for event in pygame.event.get():
            #Keydown
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == K_BACKSLASH:
                    if video.getFullscreen() == False:
                        video.SetDisplay(800, 600, True)
                        Loop_Count_GameOver = 0
                    else:
                        video.SetDisplay(800, 600, False)
                        Loop_Count_GameOver = 0

            if event.type == JOYBUTTONDOWN:
                if event.button == 3:
                    pygame.quit()
                    sys.exit(0)
                if event.button == 1:
                    if video.getFullscreen() == False:
                        video.SetDisplay(800, 600, True)
                    else:
                        video.SetDisplay(800, 600, False)

        enemy_man.Render()
        video.SCREEN.fill((0,0,0))

        #pygame.display.get_surface().blit(GameOver_Text, (400,300))
        pygame.display.get_surface().blit(GameOver_Image, (0,0))
        pygame.display.get_surface().blit(Score_Surface, (425, 344))
        pygame.display.get_surface().blit(Life_Surface, (425, 382))
        pygame.display.get_surface().blit(enemy_man.tmpSurface, (0,65))

        #Clear screen before rendering
        pygame.display.flip()

        if Loop_Count_GameOver < 1:
            pygame.display.flip()

        #Update Game Over Loop Count
        Loop_Count_GameOver += 1

    ##################################
    Loop_Count += 1 #Update Count
