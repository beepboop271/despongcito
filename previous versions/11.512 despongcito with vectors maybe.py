import pygame
import random
import math

pygame.init()

# --- FUNCTIONS FOR VARIABLES --- #
def calculateOffset(value, minMaxArray):
    return (100*(value-minMaxArray[MIN]))/(minMaxArray[MAX]-minMaxArray[MIN])

def createFont(font, size):
    newFont = pygame.font.SysFont(font, size)
    return newFont

def loadImage(image):
    newImage = pygame.image.load(image).convert()
    return newImage

def loadImageTransparent(image):
    newImage = pygame.image.load(image).convert_alpha()
    return newImage

# --- Variables and Constants --- #

SPEED_POLL_INTERVAL = 100
pollDistance = 200
GET_POSITION = pygame.USEREVENT  # custom event
pygame.time.set_timer(GET_POSITION, SPEED_POLL_INTERVAL)
clock = pygame.time.Clock()

MIN = 0             # To make array indexes easier to read/understand
MAX = 1             # e.g. to find the minimum possible value for the radius,
RADIUS = 0          # instead of radiusRange[0] it is now radiusRange[MIN]
PADDLE = 1          #
LENGTH = 0          #
HEIGHT = 1          #
X = 0               #
Y = 1               #
NO_FACE = 0         #
LEFT_FACE = 1       #
TOP_FACE = 2        #
TL_CORNER = 3       #
BOTTOM_FACE = 4     #
BL_CORNER = 5       #
RIGHT_FACE = 6      #
TR_CORNER = 7       #
BR_CORNER = 8       #

arial25 = createFont("arial", 25)
comicSans20 = createFont("Comic Sans MS", 20)
impact70 = createFont("Impact", 70)
impact50 = createFont("Impact", 50)
impact25 = createFont("Impact", 25)
comicSans10 = createFont("Comic Sans MS", 10)

width = 800
height = 600
ballRadius = 15  # 1 to 100
DEFAULT_RADIUS = 15
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

# Declare unit normals: vectors perpendicular to the surface they rest on with magnitude 1
FACE_NORMALS = [None]*9
FACE_NORMALS[NO_FACE] = 0
FACE_NORMALS[LEFT_FACE] = pygame.math.Vector2(1, 0)
FACE_NORMALS[TOP_FACE] = pygame.math.Vector2(0, -1)
FACE_NORMALS[TL_CORNER] = pygame.math.Vector2(-1, 1)
FACE_NORMALS[BOTTOM_FACE] = pygame.math.Vector2(0, 1)
FACE_NORMALS[BL_CORNER] = pygame.math.Vector2(-1, -1)
FACE_NORMALS[RIGHT_FACE] = pygame.math.Vector2(-1, 0)
FACE_NORMALS[TR_CORNER] = pygame.math.Vector2(1, 1)
FACE_NORMALS[BR_CORNER] = pygame.math.Vector2(1, -1)

dy = 6
dDy = 0.7
dDDy = 0.1
frictionDDY = 0.5
frictionDDDY = 0.07  # don't think friction even applies to jerk but oh well, need something to reduce it
vMax = 20
aMax = 5
vGuest = 0
aGuest = 0
vHost = 0
aHost = 0
ballSpeed = 4
# Determines how the paddles respond and move to keyboard input. The first 3 derivatives of position are available
# Velocity changes the position of the paddles at a certain rate
# Acceleration changes the velocity of the paddles at a certain rate
# Jerk changes the acceleration of the paddles at a certain rate
paddleMode = "Velocity"  # "Jerk" or "Acceleration" or "Velocity"

guestVec = pygame.math.Vector2(0, vGuest)
hostVec = pygame.math.Vector2(0, vHost)

window = "Title"

running = True
sliderInFocus = [False, False]

# ----------------------------------------- #

# --- MAIN FUNCTIONS --- #

def resetBall():
    # Places the ball in the middle and gives it a random direction
    vec = pygame.math.Vector2(random.choice([-1, 1]), (random.random()+0.2)*random.choice([-1, 1]))
    vec.scale_to_length(ballSpeed)
    return width/2, height/2, vec

def resetGame():
    # Resets all the game values
    # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
    ballX, ballY, ballVec = resetBall()
    return 0, 0, ballX, ballY, ballVec, height/2, height/2, height/2, height/2, 0, 0

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
    # Returns the x and y of an image for it to be centered
    imageCenter = image.get_rect().center
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
    # Draws the actual moving parts
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
    display.blit(guestScore, (width/4+50, 10))
    display.blit(hostScore, (width/4*2.6, 10))

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
    display.blit(*drawCenteredText(width/2, 50, "SETTINGS", impact70, BLACK))

    # Ball radius 1-100
    display.blit(*drawCenteredText(width/2, 120, "Ball Radius (px):", comicSans20, BLACK))
    ballRadiusSlider = drawSlider(width/2, 150, 100, radiusSetting, 10, radiusRange[MIN], radiusRange[MAX])  # accesing global scope maybe fix later

    # Paddle length 10-200
    display.blit(*drawCenteredText(width/2, 230, "Paddle Length (px):", comicSans20, BLACK))
    paddleLengthSlider = drawSlider(width/2, 260, 100, lengthSetting, 10, paddleRange[MIN], paddleRange[MAX])  # accesing global scope maybe fix later

    backButton = drawCenteredButton(width/6, 550, "Back", comicSans20, BLACK, WHITE, 10)
    resetRadius = drawCenteredButton(width/2, 180, "Reset", comicSans10, BLACK, WHITE, 5)
    resetLength = drawCenteredButton(width/2, 290, "Reset", comicSans10, BLACK, WHITE, 5)

    return ballRadiusSlider, paddleLengthSlider, backButton, resetRadius, resetLength

def drawWin(hostScore, guestScore):
    if hostScore > guestScore:
        display.blit(*drawCenteredText(width/2, 70, "DESPACITO VICTORY!", impact70, BLACK))
    elif guestScore > hostScore:
        display.blit(*drawCenteredText(width/2, 70, "EVIL PRIME VICTORY!", impact70, BLACK))

    display.blit(*drawCenteredText(width/2, 150, "Host: "+str(hostScore)+" -- Guest: "+str(guestScore), impact50, BLACK))

    restartButton = drawCenteredButton(width/2, height/1.5, "Restart", comicSans20, BLACK, WHITE, 10)
    titleButton = drawCenteredButton(width/2, height/1.5+70, "Title Screen", comicSans20, BLACK, WHITE, 10)
    quitButton = drawCenteredButton(width/2, height/1.5+140, "Quit!", comicSans20, BLACK, WHITE, 10)

    return restartButton, titleButton, quitButton

def isTouchingGuest(paddleY, paddleLength, x, y, r):
    return (x-r) < (15+paddleLength/4) and (y > paddleY and y < (paddleY+paddleLength))

def isTouchingHost(paddleY, paddleLength, x, y, r):
    return (x+r) > (width-15-paddleLength/4) and (y > paddleY and y < (paddleY+paddleLength))

# def getCollidingHostFace(paddleY, paddleLength, x, y, r):
#     # this is a mess
#     xL = width-15-paddleLength/4
#     xR = width-15
#     yT = paddleY
#     yB = paddleY+paddleLength
#     corner = int(ballSpeed*1.5)
#     face = NO_FACE
#     if y > yT+corner and y < yB-corner and x+r < xL+int(ballSpeed*2) and x+r > xL:
#         face = LEFT_FACE
#     elif y+r > yT and y+r < yT+corner and x < xR and x > xL+corner:
#         face = TOP_FACE
#     elif y+r > yT and y+r < yT+corner and x+r < xL+corner and x+r > xL:
#         face = TL_CORNER
#     elif y-r > yB-corner and y-r < yB and x < xR and x > xL+corner:
#         face = BOTTOM_FACE
#     elif y-r > yB-corner and y-r < yB and x+r < xL+corner and x+r > xL:
#         face = BL_CORNER
#     print face
#     return face
def getCollidingHostFace(x, y, paddleY, paddleLength):
    # this is a mess
    rectWidth = paddleLength/4
    xL = width-15-rectWidth
    yT = paddleY
    yB = paddleY+paddleLength
    corner = ballRadius
    face = -1
    if pygame.Rect(xL, yT+corner, ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = LEFT_FACE
    elif pygame.Rect(xL+corner, yT, rectWidth-corner, corner).collidepoint(x, y):
        face = TOP_FACE
    elif pygame.Rect(xL, yT, corner, corner).collidepoint(x, y):
        face = TL_CORNER
    elif pygame.Rect(xL+corner, yB-corner, rectWidth-corner, corner).collidepoint(x, y):
        face = BOTTOM_FACE
    elif pygame.Rect(xL, yB-corner, corner, corner).collidepoint(x, y):
        face = BL_CORNER
    elif pygame.Rect(xL+ballRadius*1.5, yT+corner, rectWidth-ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = NO_FACE
    print face
    return face

# def getCollidingGuestFace(paddleY, paddleLength, x, y, r):
#     # this is a mess
#     xL = 15
#     xR = 15+paddleLength/4
#     yT = paddleY
#     yB = paddleY+paddleLength
#     corner = int(ballSpeed*1.5)
#     face = NO_FACE
#     if y > yT+corner and y < yB-corner and x-r > xR-int(ballSpeed*2) and x-r < xR:
#         face = RIGHT_FACE
#     elif y+r > yT and y+r < yT+corner and x > xL and x < xR-corner:
#         face = TOP_FACE
#     elif y+r > yT and y+r < yT+corner and x-r > xR-corner and x-r < xR:
#         face = TR_CORNER
#     elif y-r > yB-corner and y-r < yB and x > xL and x < xL-corner:
#         face = BOTTOM_FACE
#     elif y-r > yB-corner and y-r < yB and x-r > xR-corner and x-r < xR:
#         face = BR_CORNER
#     print face
#     return face
def getCollidingGuestFace(x, y, paddleY, paddleLength):
    # this is a mess
    rectWidth = paddleLength/4
    xL = 15
    xR = 15+rectWidth
    yT = paddleY
    yB = paddleY+paddleLength
    corner = ballRadius
    face = -1
    if pygame.Rect(xR-ballRadius*1.5, yT+corner, ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = RIGHT_FACE
    elif pygame.Rect(xL, yT, rectWidth-corner, corner).collidepoint(x, y):
        face = TOP_FACE
    elif pygame.Rect(xR-corner, yT, corner, corner).collidepoint(x, y):
        face = TR_CORNER
    elif pygame.Rect(xL, yB-corner, rectWidth-corner, corner).collidepoint(x, y):
        face = BOTTOM_FACE
    elif pygame.Rect(xR-corner, yB-corner, corner, corner).collidepoint(x, y):
        face = BR_CORNER
    elif pygame.Rect(xL, yT+corner, rectWidth-ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = NO_FACE
    print face
    return face

def closestPoint(cX, cY, r, rX, rY, rW, rL):
    # Given a circle with radius r centered at (cX, cY) and a rectangle with top-left corner at (rX, rY) with width (x) rW and length (y) rL,
    # return the point on the rectangle closest to the circle
    # Adapted from https://yal.cc/rectangle-circle-intersection-test/
    x = constrainValue(cX, rX, rX+rW)
    y = constrainValue(cY, rY, rY+rL)
    return x, y

def distance(x1, y1, x2, y2):
    # Returns the distance between (x1, y1) and (x2, y2) if no radius is supplied.
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def constrainValue(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value

def offsetToValue(offset, range):
    # Calculates a value based on the offset (0 to 100) of the slider marker in the range of possible values for that setting
    return (offset/100.0)*(range[MAX]-range[MIN])+range[MIN]

def processTitleEvents(events):
    window, running = "Title", True
    for event in events:
        if event.type == pygame.MOUSEBUTTONUP:  # Use mouse up because most applications trigger clicks on mouse up
            if isInside(playButton):
                window = "Game"
            elif isInside(settingsButton):
                window = "Settings"
            elif isInside(quitButton):
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                window = "Game"
    return window, running

def processGameEvents(events):
    window = "Game"
    shouldFindSpeed = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window = "Pause"
        elif event.type == GET_POSITION and (ballX > (width-pollDistance) or ballX < pollDistance):
            shouldFindSpeed = True
    return window, shouldFindSpeed

def processPauseEvents(events):
    window, running = "Pause", True
    shouldRestart = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window = "Game"
                pygame.time.wait(500)
        elif event.type == pygame.MOUSEBUTTONUP:
            if isInside(resumeButton):
                window = "Game"
                pygame.time.wait(500)
            elif isInside(restartButton):
                window = "Game"
                shouldRestart = True
                pygame.time.wait(500)
            elif isInside(settingsButton):
                window = "Settings"
            elif isInside(quitButton):
                running = False
    return window, running, shouldRestart

def processWinEvents(events):
    window, running = "Win", True
    shouldRestart = False

    for event in events:
        if event.type == pygame.MOUSEBUTTONUP:
            if isInside(restartButton):
                window = "Game"
                shouldRestart = True
                pygame.time.wait(500)
            elif isInside(titleButton):
                window = "Title"
                shouldRestart = True
            elif isInside(quitButton):
                running = False
    return window, running, shouldRestart

def calculateMovement(angle, distance):
    # Calculate the offset in x and y required to move the ball a fixed distance at a given angle
    dx = distance*math.cos(angle)
    dy = distance*math.sin(angle)
    return dx, dy

def drawVector(vector, x, y):
    # Draws the vector given centered at (x,y)
    # for testing
    # pygame.draw.line(display, WHITE, (x, y), (x+(vector.x*8), y+(vector.y*8)), 7)
    pygame.draw.line(display, BLACK, (x, y), (x+vector.x, y+vector.y), 2)

def applyFriction(rate, friction):
    if abs(rate) >= friction:
        rate = rate+math.copysign(friction, -rate)
    else:
        rate = 0
    return rate

# --------------------------- #

display = initDisplay(width, height)

gameBackground = loadImage("spaceBack.png")
titleScreen = loadImage("titleScreen.png")
hostWinBackground = loadImage("hostBackground.png")
guestWinBackground = loadImage("guestBackground.png")

pauseBackground = loadImageTransparent("pauseScreenBack1.png")
gameLogo = loadImageTransparent("oofLogo.png")
titleBarrier = loadImageTransparent("titleBarrier.png")
titleText = loadImageTransparent("despongcito3.png")
despaSpider = loadImageTransparent("despongcitoSpider.png")
settingScreen = loadImageTransparent("settingScreen.png")

pygame.display.set_caption("Despongcito 3: In Space (Deluxe Edition) (Collector's Edition)")
pygame.display.set_icon(gameLogo)

pastWindow = ""

# This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()
print ballVec
# --- Main Loop --- #

while running:
    if hostScore >= 7:
        display.blit(hostWinBackground, (0, 0))
        window = "Win"
    if guestScore >= 7:
        display.blit(guestWinBackground, (0, 0))
        window = "Win"

    if window == "Game":
        # Draw everything
        pastWindow = "Game"
        display.blit(gameBackground, (0, 0))
        drawScoreboard(hostScore, guestScore)
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)

        # for testing
        pygame.draw.line(display, WHITE, (pollDistance, 0), (pollDistance, height))
        pygame.draw.line(display, WHITE, (width-pollDistance, 0), (width-pollDistance, height))
        drawVector(ballVec, ballX, ballY)
        drawVector(guestVec, 15+paddleLength/8, guestY+paddleLength/2)
        drawVector(hostVec, width-15-paddleLength/8, hostY+paddleLength/2)

        pygame.draw.rect(display, (255, 0, 0), (15+paddleLength/4-ballRadius*1.5, guestY+ballRadius, ballRadius*1.5, paddleLength-2*ballRadius), 2)
        pygame.draw.rect(display, (0, 255, 0), (15, guestY, paddleLength/4-ballRadius, ballRadius), 2)
        pygame.draw.rect(display, (0, 0, 255), (15+paddleLength/4-ballRadius, guestY, ballRadius, ballRadius), 2)
        pygame.draw.rect(display, (255, 255, 0), (15, guestY+paddleLength-ballRadius, paddleLength/4-ballRadius, ballRadius), 2)
        pygame.draw.rect(display, (0, 255, 255), (15+paddleLength/4-ballRadius, guestY+paddleLength-ballRadius, ballRadius, ballRadius), 2)
        pygame.draw.rect(display, (255, 0, 255), (15, guestY+ballRadius, paddleLength/4-ballRadius*1.5, paddleLength-2*ballRadius), 2)

        ballX = ballX+ballVec.x
        ballY = ballY+ballVec.y

        # Check if the ball has hit a wall
        if ballY <= (0+ballRadius):
            ballVec = ballVec.reflect(FACE_NORMALS[BOTTOM_FACE])
        elif ballY >= (height-ballRadius):
            ballVec = ballVec.reflect(FACE_NORMALS[TOP_FACE])
        # Check if the ball has hit a paddle
        if ballX < width/2:
            # guest
            collideX, collideY = closestPoint(ballX, ballY, ballRadius, 15, guestY, paddleLength/4, paddleLength)
            pygame.draw.line(display, BLACK, (ballX, ballY), (collideX, collideY), 2)  # for testing
            d = distance(collideX, collideY, ballX, ballY)
            print d, d < ballRadius, ballRadius
            if d < ballRadius:
                face = getCollidingGuestFace(collideX, collideY, guestY, paddleLength)
                if face != -1:
                    ballVec = ballVec.reflect(FACE_NORMALS[face])+guestVec
                    ballVec.scale_to_length(ballSpeed)
        else:
            # host
            collideX, collideY = closestPoint(ballX, ballY, ballRadius, width-15-paddleLength/4, hostY, paddleLength/4, paddleLength)
            pygame.draw.line(display, BLACK, (ballX, ballY), (collideX, collideY), 2)  # for testing
            if distance(collideX, collideY, ballX, ballY) < ballRadius:
                face = getCollidingHostFace(collideX, collideY, hostY, paddleLength)
                if face != -1:
                    ballVec = ballVec.reflect(FACE_NORMALS[face])+hostVec
                    ballVec.scale_to_length(ballSpeed)

        # if isTouchingGuest(guestY, paddleLength, ballX, ballY, ballRadius):
        #     face = getCollidingGuestFace(guestY, paddleLength, ballX, ballY, ballRadius)
        #     if face != 0:
        #         ballVec = ballVec.reflect(FACE_NORMALS[face])
        # elif isTouchingHost(hostY, paddleLength, ballX, ballY, ballRadius):
        #     face = getCollidingHostFace(hostY, paddleLength, ballX, ballY, ballRadius)
        #     if face != 0:
        #         ballVec = ballVec.reflect(FACE_NORMALS[face])

        # Check if the ball is touching a paddle
        # if isTouchingGuest(guestY, paddleLength, ballX, ballY, ballRadius):
        #     ballDX = -ballDX
        #     ballDY = ballDY+((guestSpeed/600.0)**3)
        # elif isTouchingHost(hostY, paddleLength, ballX, ballY, ballRadius):
        #     ballDX = -ballDX
        #     ballDY = ballDY+((hostSpeed/600.0)**3)

        # Check if the ball has gone past a paddle
        if ballX+ballRadius < -10:
            ballX, ballY, ballVec = resetBall()
            hostScore = hostScore+1
            pygame.time.wait(500)
        if ballX-ballRadius > width+10:
            ballX, ballY, ballVec = resetBall()
            guestScore = guestScore+1
            pygame.time.wait(500)

        # Get the keyboard input
        keys = pygame.key.get_pressed()
        # if paddleMode == "Velocity":
        #     # Move paddles at a certain speed if keys are pressed
        #     if keys[guestUp]:
        #         guestY = constrainValue(guestY-dy, 0, height-paddleLength)
        #     if keys[guestDown]:
        #         guestY = constrainValue(guestY+dy, 0, height-paddleLength)
        #     if keys[hostUp]:
        #         hostY = constrainValue(hostY-dy, 0, height-paddleLength)
        #     if keys[hostDown]:
        #         hostY = constrainValue(hostY+dy, 0, height-paddleLength)
        if paddleMode == "Velocity":
            if keys[guestUp]:
                vGuest = -dy
            if keys[guestDown]:
                vGuest = dy
            if keys[hostUp]:
                vHost = -dy
            if keys[hostDown]:
                vHost = dy

            guestVec = pygame.math.Vector2(0, vGuest)
            hostVec = pygame.math.Vector2(0, vHost)

            guestY = constrainValue(guestY+vGuest, 0, height-paddleLength)
            hostY = constrainValue(hostY+vHost, 0, height-paddleLength)
            vGuest = 0
            vHost = 0
        elif paddleMode == "Acceleration":
            # Accelerate paddles at a certain rate if keys are pressed
            if keys[guestUp]:
                vGuest = constrainValue(vGuest-dDy, -vMax, vMax)
            if keys[guestDown]:
                vGuest = constrainValue(vGuest+dDy, -vMax, vMax)
            if keys[hostUp]:
                vHost = constrainValue(vHost-dDy, -vMax, vMax)
            if keys[hostDown]:
                vHost = constrainValue(vHost+dDy, -vMax, vMax)
            # Accelerate paddles the opposite direction (apply friction) at all times
            vGuest = applyFriction(vGuest, frictionDDY)
            vHost = applyFriction(vHost, frictionDDY)
            # Update vectors
            guestVec = pygame.math.Vector2(0, vGuest)
            hostVec = pygame.math.Vector2(0, vHost)
            # Move the paddles by the current velocity
            guestY = constrainValue(guestY+vGuest, 0, height-paddleLength)
            hostY = constrainValue(hostY+vHost, 0, height-paddleLength)
        elif paddleMode == "Jerk":
            # Jerk (change acceleration) paddles at a certain rate if keys are pressed
            if keys[guestUp]:
                aGuest = constrainValue(aGuest-dDDy, -aMax, aMax)
            if keys[guestDown]:
                aGuest = constrainValue(aGuest+dDDy, -aMax, aMax)
            if keys[hostUp]:
                aHost = constrainValue(aHost-dDDy, -aMax, aMax)
            if keys[hostDown]:
                aHost = constrainValue(aHost+dDDy, -aMax, aMax)

            aGuest = applyFriction(aGuest, frictionDDDY)
            aHost = applyFriction(aHost, frictionDDDY)
            vGuest = vGuest+aGuest
            vHost = vHost+aHost

            vGuest = applyFriction(vGuest, frictionDDY)
            vHost = applyFriction(vHost, frictionDDY)
            guestVec = pygame.math.Vector2(0, vGuest)
            hostVec = pygame.math.Vector2(0, vHost)
            guestY = constrainValue(guestY+vGuest, 0, height-paddleLength)
            hostY = constrainValue(hostY+vHost, 0, height-paddleLength)

        window, shouldFindSpeed = processGameEvents(pygame.event.get())
        # if shouldFindSpeed:
        #     guestSpeed = (1000.0/SPEED_POLL_INTERVAL)*(guestY-lastGuestY)
        #     hostSpeed = (1000.0/SPEED_POLL_INTERVAL)*(hostY-lastHostY)
        #     lastGuestY = guestY
        #     lastHostY = hostY
        #     # print guestSpeed, hostSpeed

    elif window == "Pause":
        display.blit(gameBackground, (0, 0))
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        resumeButton, restartButton, settingsButton, quitButton = drawPause()
        pastWindow = "Pause"

        window, running, shouldReset = processPauseEvents(pygame.event.get())
        if shouldReset:
            # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
            hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()

    elif window == "Win":
        restartButton, titleButton, quitButton = drawWin(hostScore, guestScore)

        window, running, shouldReset = processWinEvents(pygame.event.get())
        if shouldReset:
            # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
            hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()

    elif window == "Title":
        display.blit(titleScreen, (0, 0))
        display.blit(*drawCenteredImage(width/2, height/2, despaSpider))
        display.blit(*drawCenteredImage(width/2, height/2, titleBarrier))
        display.blit(*drawCenteredImage(width/2, height/2.5, titleText))
        playButton, settingsButton, quitButton = drawTitle()
        pastWindow = "Title"

        window, running = processTitleEvents(pygame.event.get())

    elif window == "Settings":
        display.blit(settingScreen, (0, 0))
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        radiusSlider, paddleSlider, backButton, resetRadius, resetLength = drawSettings(radiusOffset, paddleOffset)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    window = pastWindow
            elif event.type == pygame.MOUSEMOTION:
                if (isInside(radiusSlider) or sliderInFocus[RADIUS]) and event.buttons[0] == 1:
                    sliderInFocus[RADIUS] = True
                    pygame.mouse.set_visible(False)
                    radiusOffset = radiusOffset+event.rel[0]
                    radiusOffset = constrainValue(radiusOffset, 0, 100)
                    ballRadius = offsetToValue(radiusOffset, radiusRange)
                elif (isInside(paddleSlider) or sliderInFocus[PADDLE]) and event.buttons[0] == 1:
                    sliderInFocus[PADDLE] = True
                    pygame.mouse.set_visible(False)
                    paddleOffset = paddleOffset+event.rel[0]
                    paddleOffset = constrainValue(paddleOffset, 0, 100)
                    paddleLength = offsetToValue(paddleOffset, paddleRange)
            elif event.type == pygame.MOUSEBUTTONUP:
                pygame.mouse.set_visible(True)  # Make the mouse visible once the mouse has clicked off any slider
                for i in range(len(sliderInFocus)):
                    sliderInFocus[i] = False
                if isInside(backButton):
                    window = pastWindow
                elif isInside(resetRadius):
                    ballRadius = DEFAULT_RADIUS
                    radiusOffset = DEFAULT_RADIUS
                elif isInside(resetLength):
                    paddleLength = DEFAULT_LENGTH
                    lengthOffset = DEFAULT_LENGTH

    clock.tick(40)
    pygame.display.update()
# ---------------- #
pygame.quit()
