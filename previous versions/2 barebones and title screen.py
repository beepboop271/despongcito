import pygame

width = 800
height = 600

guestY = height/2
hostY = height/2

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (150,150,150)

pygame.init()
clock = pygame.time.Clock()

arial = pygame.font.SysFont("arial", 25) #todo: replace with other font??

def initDisplay(width, height):
    return pygame.display.set_mode((width,height))

display = initDisplay(width, height)

guestUp = pygame.K_w
guestDown = pygame.K_s
hostUp = pygame.K_i
hostDown = pygame.K_k
ballRadius = 10

dy = 2

#titleText = pygame.image.load("title text.png") #todo: get picture

def drawCenteredButton(x, y, text, font, buttonColour, textColour, buttonPadding): #Draws a button with centered text on a rectangle with a center of (x,y)
    textSize = font.size(text)
    textToRender = font.render(text, 1, textColour)
    buttonRect = pygame.draw.rect(display, buttonColour, (x-textSize[0]/2-buttonPadding, y-textSize[1]/2-buttonPadding, textSize[0]+2*buttonPadding, textSize[1]+2*buttonPadding))
    display.blit(textToRender, (x-textSize[0]/2, y-textSize[1]/2))
    return buttonRect

def isPressed(buttonRect):
    return buttonRect.collidepoint(pygame.mouse.get_pos())

def drawTitle():
    #display.blit(titleText, (width/3, 20)) #todo: fix dest. coords once file has been made
    playButton = drawCenteredButton(width/2, height/2, "Start!", arial, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+70, "Settings", arial, BLACK, WHITE, 7)
    return playButton, settingsButton

window = "Title"
running = True
while running:
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
    
    display.fill(GRAY)
    if window == "Game":
        drawGame()
    elif window == "Pause":
        drawPause()
    elif window == "Title":
        playButton, settingsButton = drawTitle()
    clock.tick(120)
    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[guestUp]:
        guestY = guestY-dy
    if keys[guestDown]:
        guestY = guestY+dy
    if keys[hostUp]:
        hostY = hostY-dy
    if keys[hostDown]:
        hostY = hostY+dy

pygame.quit()

