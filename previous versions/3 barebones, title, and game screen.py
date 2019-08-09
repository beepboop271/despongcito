import pygame
import time
import random

pygame.init()

clock = pygame.time.Clock()

width = 800
height = 600

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

arial = pygame.font.SysFont("arial", 25) #todo: replace with other font??

guestUp = pygame.K_w
guestDown = pygame.K_s
hostUp = pygame.K_i
hostDown = pygame.K_k

ballRadius = 20
paddleLength = 80

dy = 6

ballSpeed = 4
def resetBall():
    pygame.time.delay(500)
    return width/2, height/2, random.choice([-ballSpeed,ballSpeed]), random.random()*random.choice([-3, 3])

def initDisplay(width, height):
    return pygame.display.set_mode((width,height))

#titleText = pygame.image.load("title text.png") #todo: get picture

def drawCenteredButton(x, y, text, font, buttonColour, textColour, buttonPadding): #Draws a button with centered text on a rectangle with a center of (x,y)
    textSize = font.size(text)
    textToRender = font.render(text, 1, textColour)
    buttonRect = pygame.draw.rect(display, buttonColour, (x-textSize[0]/2-buttonPadding, y-textSize[1]/2-buttonPadding, textSize[0]+2*buttonPadding, textSize[1]+2*buttonPadding))
    display.blit(textToRender, (x-textSize[0]/2, y-textSize[1]/2))
    return buttonRect

def isPressed(buttonRect):
    #Checks if the mouse is within a given rectangle
    return buttonRect.collidepoint(pygame.mouse.get_pos())

def drawTitle():
    #display.blit(titleText, (width/3, 20)) #todo: fix dest. coords once file has been made
    playButton = drawCenteredButton(width/2, height/2, "Start!", arial, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+70, "Settings", arial, BLACK, WHITE, 7)
    return playButton, settingsButton

def drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius):
    pygame.draw.rect(display, WHITE, (15, guestY, paddleLength/4, paddleLength))
    pygame.draw.rect(display, WHITE, (width-15-paddleLength/4, hostY, paddleLength/4, paddleLength))
    pygame.draw.ellipse(display, WHITE, (ballX-ballRadius, ballY-ballRadius, 2*ballRadius, 2*ballRadius)) #shift everything so the x,y references the center

def isTouchingGuest(paddleY, paddleLength, x, y, r):
    return (x-r)<=(15+paddleLength/4) and (y>=paddleY and y<=(paddleY+paddleLength))

def isTouchingHost(paddleY, paddleLength, x, y, r):
    return (x+r)>=(width-15-paddleLength/4) and (y>=paddleY and y<=(paddleY+paddleLength))

display = initDisplay(width, height)
window = "Title"
running = True
START_TIME = time.time()
ballX, ballY, ballDX, ballDY = resetBall()
while running:

    display.fill(GRAY)
    if window == "Game":
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

        if ballX+ballRadius<0 or ballX-ballRadius>width:
            ballX, ballY, ballDX, ballDY = resetBall()
        
        keys = pygame.key.get_pressed()
        if keys[guestUp]:
            guestY = guestY-dy
        if keys[guestDown]:
            guestY = guestY+dy
        if keys[hostUp]:
            hostY = hostY-dy
        if keys[hostDown]:
            hostY = hostY+dy
    elif window == "Pause":
        drawPause()
    elif window == "Title":
        playButton, settingsButton = drawTitle()
    clock.tick(120)
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False #for testing/development
                #window = "Pause"
        if event.type == pygame.MOUSEBUTTONUP:
            if isPressed(playButton):
                window = "Game"
            if isPressed(settingsButton):
                window = "Pause"
        if event.type == GET_POSITION and window == "Game":
            guestSpeed = (1000.0/SPEED_POLL_INTERVAL)*(guestY-lastGuestY)
            hostSpeed = (1000.0/SPEED_POLL_INTERVAL)*(hostY-lastHostY)
            lastGuestY = guestY
            lastHostY = hostY
            print guestSpeed, hostSpeed

pygame.quit()
