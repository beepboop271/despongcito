import pygame
import time
import random

pygame.init()

clock = pygame.time.Clock()

#--- Game screen settings ---#
width = 800
height = 600
#-------------------------------------#

#--- Variables and Constants ---#
SPEED_POLL_INTERVAL = 500
GET_POSITION = pygame.USEREVENT
pygame.time.set_timer(GET_POSITION, SPEED_POLL_INTERVAL)

guestY = height/2
hostY = height/2
ballX = width/2
ballY = height/2

lastGuestY = height/2
lastHostY = height/2
guestSpeed = 0
hostSpeed = 0

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (150,150,150)

arial = pygame.font.SysFont("arial", 25) #todo: replace with other font?? YES
comicSans = pygame.font.SysFont("Comic Sans MS", 20)
impact = pygame.font.SysFont("Impact", 70)
fontScore = pygame.font.SysFont("Impact", 25)

gameBackground = pygame.image.load("spaceBack.png")
pauseBackground = pygame.image.load("pauseScreenBack1.png")
gameLogo = pygame.image.load("oofLogo.png")

guestUp = pygame.K_w
guestDown = pygame.K_s
hostUp = pygame.K_i
hostDown = pygame.K_k

hostScore = 0
guestScore = 0

ballRadius = 20
paddleLength = 80

dy = 6
ballSpeed = 4

#-----------------------------------------#


#--- FUNCTIONS ---#
def resetBall():
    #Resets the ball and places it in the middle, allows it to go in a random direction
    pygame.time.delay(500)
    return width/2, height/2, random.choice([-ballSpeed,ballSpeed]), random.random()*random.choice([-3, 3])

#----------------------#
def initDisplay(width, height):
    #Sets the initial display"
    return pygame.display.set_mode((width,height))

#----------------------#
#titleText = pygame.image.load("title text.png") #todo: get picture
#----------------------#
def drawCenteredButton(x, y, text, font, buttonColour, textColour, buttonPadding):
    #Draws a button with centered text on a rectangle with a center of (x,y)
    textSize = font.size(text)
    textToRender = font.render(text, 1, textColour)
    buttonRect = pygame.draw.rect(display, buttonColour, (x-textSize[0]/2-buttonPadding, y-textSize[1]/2-buttonPadding, textSize[0]+2*buttonPadding, textSize[1]+2*buttonPadding))
    display.blit(textToRender, (x-textSize[0]/2, y-textSize[1]/2))
    return buttonRect

#----------------------#
def isPressed(buttonRect):
    #Checks if the mouse is within a given rectangle (The button)
    return buttonRect.collidepoint(pygame.mouse.get_pos())

#----------------------#
def drawTitle():
    #display.blit(titleText, (width/3, 20)) #todo: fix dest. coords once file has been made
    playButton = drawCenteredButton(width/2, height/2, "Start!", comicSans, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+70, "Settings", comicSans, BLACK, WHITE, 10)
    quitButton = drawCenteredButton(width/2, height/2+140, "Quit!", comicSans, BLACK, WHITE, 10)
    return playButton, settingsButton, quitButton

#----------------------#
def drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius):
    pygame.draw.rect(display, WHITE, (15, guestY, paddleLength/4, paddleLength))
    pygame.draw.rect(display, WHITE, (width-15-paddleLength/4, hostY, paddleLength/4, paddleLength))
    pygame.draw.ellipse(display, WHITE, (ballX-ballRadius, ballY-ballRadius, 2*ballRadius, 2*ballRadius)) #shift everything so the x,y references the center
    
#----------------------#
def drawPause():
##    display.blit(gameBackground, (0,0))
    display.fill(GRAY)
    pygame.draw.rect(display, WHITE, (15, guestY, paddleLength/4, paddleLength))
    pygame.draw.rect(display, WHITE, (width-15-paddleLength/4, hostY, paddleLength/4, paddleLength))
    pygame.draw.ellipse(display, WHITE, (ballX-ballRadius, ballY-ballRadius, 2*ballRadius, 2*ballRadius))
    display.blit(pauseBackground, (0,0))
    pauseTitle = impact.render("PAUSED", 1, BLACK)
    display.blit(pauseTitle, (width / 2.75, 30))
    
    titleButton = drawCenteredButton(width/2, height/2-20, "Title Screen", comicSans, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+50, "Settings", comicSans, BLACK, WHITE, 10)
    quitButton = drawCenteredButton(width/2, height/2+120, "Quit!", comicSans, BLACK, WHITE, 10)
    return titleButton, settingsButton, quitButton

#----------------------#
def drawScoreboard(hostScore, guestScore):
    hostScore = fontScore.render(str(hostScore), 1, WHITE)
    guestScore = fontScore.render(str(guestScore), 1, WHITE)
    
    pygame.draw.rect(display, GRAY, (width/4, 0, width/4*2, 50), 0)
    display.blit(hostScore, (width/4 + 50, 10))
    display.blit(guestScore, (width/4*2.6, 10))
    
#----------------------#
def resetScoreboard():
    hostScore = 0
    guestScore = 0

    return hostScore, guestScore
#----------------------#
def isTouchingGuest(paddleY, paddleLength, x, y, r):
    return (x-r)<=(15+paddleLength/4) and (y>=paddleY and y<=(paddleY+paddleLength))

#----------------------#
def isTouchingHost(paddleY, paddleLength, x, y, r):
    return (x+r)>=(width-15-paddleLength/4) and (y>=paddleY and y<=(paddleY+paddleLength))

#----------------------#

display = initDisplay(width, height)

window = "Title"

running = True
alreadyPressed = False
pygame.display.set_caption("Despongcito 3: In Space (Deluxe Edition) (Collector's Edition)")
pygame.display.set_icon(gameLogo)

START_TIME = time.time()
ballX, ballY, ballDX, ballDY = resetBall()

#--- The Loop ---#

while running:
    display.fill(GRAY)
    if window == "Game":
##        display.blit(gameBackground, (0,0))
        display.fill(GRAY)
        drawScoreboard(hostScore, guestScore)
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        ballX = ballX + ballDX
        ballY = ballY + ballDY
        if ballY<=(0+ballRadius) or ballY>=(height-ballRadius):
            ballDY = -ballDY
    
        if isTouchingGuest(guestY, paddleLength, ballX, ballY, ballRadius):
            ballDX = -ballDX
            ballDY = ballDY+(guestSpeed/150.0)
            print ballDY
        elif isTouchingHost(hostY, paddleLength, ballX, ballY, ballRadius):
            ballDX = -ballDX
            ballDY = ballDY+(hostSpeed/150.0)
            print ballDY

        if ballX+ballRadius<0:
            ballX, ballY, ballDX, ballDY = resetBall()
            guestScore += 1
            print guestScore
        if ballX-ballRadius>width:
            ballX, ballY, ballDX, ballDY = resetBall()
            hostScore += 1
            print hostScore
        
        keys = pygame.key.get_pressed()
        if keys[guestUp]:
            if guestY - dy > 0:
                 guestY = guestY-dy
        if keys[guestDown]:
            if guestY + paddleLength + dy < height:
                guestY = guestY+dy
        if keys[hostUp]:
            if hostY - dy > 0:
                hostY = hostY-dy
        if keys[hostDown]:
            if hostY + paddleLength + dy < height:
                hostY = hostY+dy
                
    elif window == "Pause":
            titleButton, settingsButton, quitButton = drawPause()
            
    elif window == "Settings":
        drawSettings()
            
    elif window == "Title":
        playButton, settingsButton, quitButton = drawTitle()
        titleButton = None
        alreadyPressed = False

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #running = False #for testing/development
                if alreadyPressed:
                    window = "Game"
                    alreadyPressed = False
                else:
                    window = "Pause"
                    alreadyPressed = True
        if event.type == pygame.MOUSEBUTTONUP:
            if isPressed(playButton):
                    window = "Game"
                    hostScore, guestScore = resetScoreboard()
                    guestY = height/2
                    hostY = height/2
                    ballX = width/2
                    ballY = height/2
            if isPressed(settingsButton):
                window = "Settings"
            if isPressed(quitButton):
                pygame.quit()
            try:
                if isPressed(titleButton):
                    window = "Title"
            except:
                None
                    
        if event.type == GET_POSITION and window == "Game":
            guestSpeed = (1000.0/SPEED_POLL_INTERVAL)*(guestY-lastGuestY)
            hostSpeed = (1000.0/SPEED_POLL_INTERVAL)*(hostY-lastHostY)
            lastGuestY = guestY
            lastHostY = hostY
            print guestSpeed, hostSpeed
            
    clock.tick(120)
    pygame.display.update()
#----------------#
pygame.quit()
