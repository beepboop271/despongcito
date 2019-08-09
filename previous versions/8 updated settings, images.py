import pygame, time, random

pygame.init()

# --- Variables and Constants --- #

# To make array indexes easier to read/understand
# e.g. to find the minimum possible value for the radius,
# instead of radiusRange[0] it is now radiusRange[MIN]

MIN = 0
MAX = 1
RADIUS = 0
PADDLE = 1
LENGTH = 0
HEIGHT = 1
X = 0
Y = 1

SPEED_POLL_INTERVAL = 100
pollDistance = 200
GET_POSITION = pygame.USEREVENT  # custom event
pygame.time.set_timer(GET_POSITION, SPEED_POLL_INTERVAL)
clock = pygame.time.Clock()

# Only used for variable declarations... idk where to put it
def calculateOffset(value, minMaxArray):
    return (100*(value-minMaxArray[MIN]))/(minMaxArray[MAX]-minMaxArray[MIN])

def createFont(font, size):
    newFont = pygame.font.SysFont(font, size)
    return newFont

arial25 = createFont('arial', 25)
comicSans20 = createFont('Comic Sans MS', 20)
impact70 = createFont('Impact', 70)
impact25 = createFont('Impact', 25)
comicSans10 = createFont('Comic Sans MS', 10)

width = 800
height = 600
ballRadius = 20  # 1 to 100
DEFAULT_RADIUS = 20
radiusRange = [1, 100]
radiusOffset = calculateOffset(ballRadius, radiusRange)
paddleLength = 80  # 10 to 200
DEFAULT_LENGTH = 80
paddleRange = [10, 200]
paddleOffset = calculateOffset(paddleLength, paddleRange)

guestUp = pygame.K_w
guestDown = pygame.K_s
hostUp = pygame.K_i
hostDown = pygame.K_k

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# titleText = pygame.image.load("title text.png") #todo: get picture

dy = 6
ballSpeed = 4

START_TIME = time.time()

window = "Title"

running = True
sliderInFocus = [False, False]

# ----------------------------------------- #

# --- FUNCTIONS --- #

def resetBall():
    # Places the ball in the middle and gives it a random direction
    return width/2, height/2, random.choice([-ballSpeed, ballSpeed]), random.random()*random.choice([-3, 3])

def resetGame():
    # Resets all the game values
    # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
    ballX, ballY, ballDX, ballDY = resetBall()
    return 0, 0, ballX, ballY, ballDX, ballDY, height/2, height/2, height/2, height/2, 0, 0

def initDisplay(width, height):
    # Restarts the display at a given resolution
    return pygame.display.set_mode((width, height))

def drawCenteredButton(x, y, text, font, buttonColour, textColour, buttonPadding):
    # Draws a button with centered text on a rectangle with a center of (x,y)
    textToRender, textCoords = drawCenteredText(x, y, text, font, textColour)
    buttonRect = pygame.draw.rect(display, buttonColour, (textCoords[X]-buttonPadding, textCoords[Y]-buttonPadding, textToRender.get_width()+2*buttonPadding, textToRender.get_height()+2*buttonPadding))
    display.blit(textToRender, textCoords)
    return buttonRect

def drawCenteredText(x, y, text, font, colour):
    # Returns a text surface as well as the coords of the top left corner if it was centered at (x,y)
    textSize = font.size(text)
    renderedText = font.render(text, 1, colour)
    textX = x-textSize[LENGTH]/2
    textY = y-textSize[HEIGHT]/2
    return renderedText, (textX, textY)

def drawCenteredImage(x, y, image):
    imageRect = image.get_rect()
    imageCenter = imageRect.center
    imageX = x-imageCenter[LENGTH]
    imageY = y-imageCenter[HEIGHT]
    return image, (imageX, imageY)

def isInside(rectangle):
    # Checks if the mouse is within a given rectangle (The button)
    return rectangle.collidepoint(pygame.mouse.get_pos())

def drawTitle():
    # display.blit(titleText, (width/3, 20)) #todo: fix dest. coords once file has been made
    playButton = drawCenteredButton(width/2, height/2, "Start!", comicSans20, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+70, "Settings", comicSans20, BLACK, WHITE, 10)
    quitButton = drawCenteredButton(width/2, height/2+140, "Quit!", comicSans20, BLACK, WHITE, 10)
    return playButton, settingsButton, quitButton

def drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius):
    pygame.draw.rect(display, WHITE, (15, guestY, paddleLength/4, paddleLength))
    pygame.draw.rect(display, WHITE, (width-15-paddleLength/4, hostY, paddleLength/4, paddleLength))
    pygame.draw.ellipse(display, WHITE, (ballX-ballRadius, ballY-ballRadius, 2*ballRadius, 2*ballRadius))  # shift everything so the x,y references the center

def drawPause():
    display.blit(pauseBackground, (0, 0))
    # The * "expands" the tuple of (surface, (x,y)) given by drawCenteredText() so
    # that instead of doing blit((surface, (x,y)), None), it does blit(surface, (x,y))
    display.blit(*drawCenteredText(width/2, 50, "PAUSED", impact70, BLACK))

    resumeButton = drawCenteredButton(width/2, height/2-90, "Resume", comicSans20, BLACK, WHITE, 10)
    restartButton = drawCenteredButton(width/2, height/2-20, "Restart", comicSans20, BLACK, WHITE, 10)
    settingsButton = drawCenteredButton(width/2, height/2+50, "Settings", comicSans20, BLACK, WHITE, 10)
    quitButton = drawCenteredButton(width/2, height/2+120, "Quit!", comicSans20, BLACK, WHITE, 10)
    return resumeButton, restartButton, settingsButton, quitButton

def drawScoreboard(hostScore, guestScore):  # todo: fix text position
    hostScore = impact25.render(str(hostScore), 1, WHITE)
    guestScore = impact25.render(str(guestScore), 1, WHITE)

    pygame.draw.rect(display, GRAY, (width/4, 0, width/4*2, 50), 0)
    display.blit(hostScore, (width/4 + 50, 10))
    display.blit(guestScore, (width/4*2.6, 10))

def drawSlider(x, y, length, currentXOffset, padding, min, max):
    # Draws a slider centered at (x,y) with a given length and a marker at currentXOffset to show the current value of the slider,
    # returning a rectangle hitbox for the slider

    # Make the hitbox
    hitbox = pygame.Rect((x-length/2-padding), y-2-padding, length+padding*2, padding*2+4)
    # Draw the actual slider
    pygame.draw.rect(display, BLACK, (x-length/2, y-2, length, 4), 0)
    # Draw the marker
    pygame.draw.rect(display, WHITE, (x-length/2+currentXOffset, y-5, 5, 10), 0)
    # Draw the min/max labels on the left/right
    leftSize = comicSans20.size(str(min))
    rightSize = comicSans20.size(str(max))
    leftText = comicSans20.render(str(min), 1, BLACK)
    rightText = comicSans20.render(str(max), 1, BLACK)
    display.blit(leftText, (x-length/2-padding-leftSize[LENGTH], y-leftSize[HEIGHT]/2))
    display.blit(rightText, (x+length/2+padding, y-rightSize[HEIGHT]/2))
    return hitbox

def drawSettings(radiusSetting, lengthSetting):
    display.blit(pauseBackground, (0, 0))
    display.blit(*drawCenteredText(width/2, 50, "SETTINGS", impact70, BLACK))

    # Ball radius 1-100
    display.blit(*drawCenteredText(width/2, 120, "Ball Radius (px):", comicSans20, BLACK))
    ballRadiusSlider = drawSlider(width/2, 150, 100, radiusSetting, 10, radiusRange[MIN], radiusRange[MAX])  # accesing global scope maybe fix later
    
    # Paddle length 10-200
    display.blit(*drawCenteredText(width/2, 230, "Paddle Length (px):", comicSans20, BLACK))
    paddleLengthSlider = drawSlider(width/2, 260, 100, lengthSetting, 10, paddleRange[MIN], paddleRange[MAX])  # accesing global scope maybe fix later

    backButton = drawCenteredButton(width/4, 550, "Back", comicSans20, BLACK, WHITE, 10)
    resetRadius = drawCenteredButton(width/2, 180, "Reset", comicSans10, BLACK, WHITE, 5)
    resetLength = drawCenteredButton(width/2, 290, "Reset", comicSans10, BLACK, WHITE, 5)
    
    return ballRadiusSlider, paddleLengthSlider, backButton, resetRadius, resetLength

def isTouchingGuest(paddleY, paddleLength, x, y, r):
    return (x-r) <= (15+paddleLength/4) and (y >= paddleY and y <= (paddleY+paddleLength))

def isTouchingHost(paddleY, paddleLength, x, y, r):
    return (x+r) >= (width-15-paddleLength/4) and (y >= paddleY and y <= (paddleY+paddleLength))

def fixValue(value):
    if value < 0:
        return 0
    elif value > 100:
        return 100
    else:
        return value

def offsetToValue(offset, range):
    # Calculates a value based on the offset (0 to 100) of the slider marker in the range of possible values for that setting
    return (offset/100.0)*(range[MAX]-range[MIN])+range[MIN]

# ---------------------- #

display = initDisplay(width, height)

gameBackground = pygame.image.load("spaceBack.png").convert()
pauseBackground = pygame.image.load("pauseScreenBack1.png").convert_alpha()
gameLogo = pygame.image.load("oofLogo.png").convert_alpha()
titleScreen = pygame.image.load("titleScreen.png").convert()
titleBarrier = pygame.image.load("titleBarrier.png").convert_alpha()
titleText = pygame.image.load("despongcito3.png").convert_alpha()
despaSpider = pygame.image.load("despongcitoSpider.png").convert_alpha() 

pygame.display.set_caption("Despongcito 3: In Space (Deluxe Edition) (Collector's Edition)")
pygame.display.set_icon(gameLogo)

pastWindow = ""

# This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
hostScore, guestScore, ballX, ballY, ballDX, ballDY, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()

# --- Main Loop --- #

while running:
    display.fill(GRAY)
    if window == "Game":
        # Draw everything
        display.blit(gameBackground, (0,0))
        drawScoreboard(hostScore, guestScore)
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)

        pygame.draw.line(display, WHITE, (pollDistance, 0), (pollDistance, height))
        pygame.draw.line(display, WHITE, (width-pollDistance, 0), (width-pollDistance, height))
        
        ballX = ballX + ballDX
        ballY = ballY + ballDY

        # Check if the ball has hit a wall
        if ballY <= (0+ballRadius) or ballY >= (height-ballRadius):
            ballDY = -ballDY

        # Check if the ball is touching a paddle
        if isTouchingGuest(guestY, paddleLength, ballX, ballY, ballRadius):
            ballDX = -ballDX
            # print guestSpeed
            ballDY = ballDY+(guestSpeed/150.0)
        elif isTouchingHost(hostY, paddleLength, ballX, ballY, ballRadius):
            ballDX = -ballDX
            # print hostSpeed
            ballDY = ballDY+(hostSpeed/150.0)

        # Check if the ball has gone past a paddle
        if ballX+ballRadius < 0:
            ballX, ballY, ballDX, ballDY = resetBall()
            guestScore += 1
            pygame.time.wait(500)
        if ballX-ballRadius > width:
            ballX, ballY, ballDX, ballDY = resetBall()
            hostScore += 1
            pygame.time.wait(500)

        # Get the keyboard input
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
        display.blit(gameBackground, (0,0))
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        resumeButton, playButton, settingsButton, quitButton = drawPause()
        pastWindow = "Pause"

    elif window == "Settings":
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        radiusSlider, paddleSlider, backButton, resetRadius, resetLength = drawSettings(radiusOffset, paddleOffset)
           
    elif window == "Title":
        display.blit(titleScreen,(0,0))
        display.blit(*drawCenteredImage(width/2, height/2, despaSpider))
        display.blit(*drawCenteredImage(width/2, height/2, titleBarrier))
        display.blit(*drawCenteredImage(width/2, height/2.5, titleText)) 
        playButton, settingsButton, quitButton = drawTitle()
        pastWindow = "Title"


    if window
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # running = False #for testing/development
                if window == "Game":
                    window = "Pause"
                elif window == "Pause":
                    window = "Game"
                    pygame.time.wait(500)
                elif window == "Settings":
                    if pastWindow == "Title":
                        window = "Title"
                    else:
                        window = "Pause"
                        
        elif event.type == pygame.MOUSEMOTION and window == "Settings":
            #print sliderInFocus
            # thinking about making this a function but i dont wanna depend on global v
            if (isInside(radiusSlider) or sliderInFocus[RADIUS]) and event.buttons[0] == 1:
                sliderInFocus[RADIUS] = True
                pygame.mouse.set_visible(False)
                radiusOffset = radiusOffset+event.rel[0]
                radiusOffset = fixValue(radiusOffset)
                ballRadius = offsetToValue(radiusOffset, radiusRange)
            elif (isInside(paddleSlider) or sliderInFocus[PADDLE]) and event.buttons[0] == 1:
                sliderInFocus[PADDLE] = True
                pygame.mouse.set_visible(False)
                paddleOffset = paddleOffset+event.rel[0]
                paddleOffset = fixValue(paddleOffset)
                paddleLength = offsetToValue(paddleOffset, paddleRange)
                
        elif event.type == pygame.MOUSEBUTTONUP:  # Use mouse up because most applications trigger clicks on mouse up
            pygame.mouse.set_visible(True)  # Make the mouse visible once the mouse has clicked off any slider
            for i in range(len(sliderInFocus)):
                sliderInFocus[i] = False

            if window == "Settings":
                if isInside(backButton):
                    window = pastWindow
                if isInside(resetRadius):
                    ballRadius = DEFAULT_RADIUS
                    radiusOffset = DEFAULT_RADIUS
                if isInside(resetLength):
                    paddleLength = DEFAULT_LENGTH
                    lengthOffset = DEFAULT_LENGTH

            if isInside(playButton):
                window = "Game"
                # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
                hostScore, guestScore, ballX, ballY, ballDX, ballDY, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()
                pygame.time.wait(500)
            if isInside(settingsButton):
                window = "Settings"
            if isInside(quitButton):
                running = False
            if window == "Pause" and isInside(resumeButton):
                window = "Game"
                pygame.time.wait(500)

                
        elif event.type == GET_POSITION and window == "Game" and (ballX > (width-pollDistance) or ballX < pollDistance):
            guestSpeed = (1000.0/SPEED_POLL_INTERVAL)*(guestY-lastGuestY)
            hostSpeed = (1000.0/SPEED_POLL_INTERVAL)*(hostY-lastHostY)
            lastGuestY = guestY
            lastHostY = hostY
            # print guestSpeed, hostSpeed

    clock.tick(100)
    pygame.display.update()
# ---------------- #
pygame.quit()
