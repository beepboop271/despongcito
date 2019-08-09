import pygame
import random
import math

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
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

clock = pygame.time.Clock()

MIN = 0             # To make array indexes easier to read/understand
MAX = 1             # e.g. to find the minimum possible value for the radius,
RADIUS = 0          # instead of radiusRange[0] it is now radiusRange[MIN]
PADDLE = 1          #
SPEED = 2           #
ANGLE = 3           #
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

pointSound = pygame.mixer.Sound('pointSound.wav')
pointSound.set_volume(0.4)
hitSound = pygame.mixer.Sound('Blip1.wav')
hitSound.set_volume(0.4)
buttonPress = pygame.mixer.Sound('buttonClick.wav')
buttonPress.set_volume(0.2)

titleMusic = "MRX - Mysterious Start.mp3"
gameMusic = "MRX - Conflict.mp3"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Declare normals: vectors perpendicular to the surface they rest on
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

vGuest = 0
aGuest = 0
vHost = 0
aHost = 0

guestVec = pygame.math.Vector2(0, vGuest)
hostVec = pygame.math.Vector2(0, vHost)

invincibilityFrame = 0  # Like an invincibility frame but for preventing the ball from bouncing
# e.g. when

window = "Title"
running = True

sliderInFocus = [False, False, False, False]
listenForKeyPress = False  # For changing keybinds: telling the event queue to get the key of the next press

# ---- editable settings ---- #

width = 800   # not done
height = 600  #

# Sliders
DEFAULT_RADIUS = 15
ballRadius = DEFAULT_RADIUS
radiusRange = [1, 100]
radiusOffset = calculateOffset(ballRadius, radiusRange)
DEFAULT_LENGTH = 100
paddleLength = DEFAULT_LENGTH
paddleRange = [10, 200]
paddleOffset = calculateOffset(paddleLength, paddleRange)
DEFAULT_SPEED = 5
ballSpeed = DEFAULT_SPEED
speedRange = [1, 20]
speedOffset = calculateOffset(ballSpeed, speedRange)
DEFAULT_ANGLE = 65
maxBallAngle = DEFAULT_ANGLE
angleRange = [5, 85]
angleOffset = calculateOffset(maxBallAngle, angleRange)

allowCornerCollisions = False

drawDebug = False

guestUp = pygame.K_w    # not done
guestDown = pygame.K_s  #
hostUp = pygame.K_i     #
hostDown = pygame.K_k   #

# not done
dy = 6
dDy = 0.7
dDDy = 0.1
frictionDDY = 0.5
frictionDDDY = 0.07  # don't think friction even applies to jerk but oh well, need something to reduce it
vMax = 20
aMax = 5

# Determines how the paddles respond and move to keyboard input. The first 3 derivatives of position are available
# Velocity changes the position of the paddles at a certain rate
# Acceleration changes the velocity of the paddles at a certain rate
# Jerk changes the acceleration of the paddles at a certain rate
paddleMode = "Acceleration"  # "Jerk" or "Acceleration" or "Velocity"

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

def drawCheckbox(x, y, size, isChecked, text, font):
    textSize = font.size(text)
    width = textSize[LENGTH]+size

    checkRect = pygame.Rect(x-width/2+textSize[LENGTH], y-size/2+2, size, size)
    display.blit(font.render(text, 1, BLACK), (x-width/2, y-textSize[HEIGHT]/2))
    pygame.draw.rect(display, BLACK, checkRect)
    if isChecked:
        display.blit(pygame.transform.smoothscale(checkmark, (size, size)), (x-width/2+textSize[LENGTH], y-size/2+2))
    return checkRect

def drawKeyInputZone(x, y, isListening):
    if isListening:
        inputRect = drawCenteredButton(x, y, "Listening...", comicSans20, BLACK, WHITE, 10)
    else:
        inputRect = drawCenteredButton(x, y, "Click to set", comicSans20, BLACK, WHITE, 10)
    return inputRect

def drawSettings(radiusSetting, lengthSetting, speedSetting, paddleMode, cornerSetting, debugSetting, angleSetting):
    display.blit(*drawCenteredText(width/2, 50, "SETTINGS", impact70, BLACK))
    topY = 100

    # Ball radius 1-100
    display.blit(*drawCenteredText(width/4, topY, "Ball Radius (px):" + "  " + str(ballRadius), comicSans20, BLACK))
    ballRadiusSlider = drawSlider(width/4, topY+25, 100, radiusSetting, 10, radiusRange[MIN], radiusRange[MAX])  # accesing global scope maybe fix later
    resetRadius = drawCenteredButton(width/4, topY+45, "Reset", comicSans10, BLACK, WHITE, 3)

    # Max angle 5-85
    display.blit(*drawCenteredText(width/4*3, topY, "Max Ball Angle (deg):" + " " + str(maxBallAngle), comicSans20, BLACK))
    maxAngleSlider = drawSlider(width/4*3, topY+25, 100, angleSetting, 10, angleRange[MIN], angleRange[MAX])
    resetAngle = drawCenteredButton(width/4, topY+45, "Reset", comicSans10, BLACK, WHITE, 3)

    # Paddle length 10-200
    display.blit(*drawCenteredText(width/4, topY+75, "Paddle Length (px):" + "  " + str(paddleLength), comicSans20, BLACK))
    paddleLengthSlider = drawSlider(width/4, topY+100, 100, lengthSetting, 10, paddleRange[MIN], paddleRange[MAX])  # accesing global scope maybe fix later
    resetLength = drawCenteredButton(width/4, topY+120, "Reset", comicSans10, BLACK, WHITE, 3)

    # Ball Speed 1-20
    display.blit(*drawCenteredText(width/4, topY+150, "Ball Speed (px/frame):" + "  " + str(ballSpeed), comicSans20, BLACK))
    ballSpeedSlider = drawSlider(width/4, topY+175, 100, speedSetting, 10, speedRange[MIN], speedRange[MAX])
    resetSpeed = drawCenteredButton(width/4, topY+195, "Reset", comicSans10, BLACK, WHITE, 3)

    # Paddle control mode
    display.blit(*drawCenteredText(width/4, topY+225, "Paddle Control Mode:", comicSans20, BLACK))
    paddleModeButton = drawCenteredButton(width/4, topY+260, paddleMode, comicSans20, BLACK, WHITE, 3)

    # Corner collisions
    cornerCollisionCheckbox = drawCheckbox(width/4, topY+300, 20, cornerSetting, "Allow Corner Collisions: ", comicSans20)

    # Draw debug
    drawDebugCheckbox = drawCheckbox(width/4, topY+325, 20, debugSetting, "Draw Debug Info: ", comicSans20)

    backButton = drawCenteredButton(width/6, 550, "Back", comicSans20, BLACK, WHITE, 10)

    return ballRadiusSlider, paddleLengthSlider, ballSpeedSlider, backButton, resetRadius, resetLength, resetSpeed, paddleModeButton, cornerCollisionCheckbox, drawDebugCheckbox, maxAngleSlider, resetAngle

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

def getNewpaddleMode(paddleMode):
    newMode = ""
    if paddleMode == "Velocity":
        newMode = "Acceleration"
    elif paddleMode == "Acceleration":
        newMode = "Jerk"
    elif paddleMode == "Jerk":
        newMode = "Velocity"

    return newMode

def isTouchingGuest(paddleY, paddleLength, x, y, r):
    return (x-r) < (15+paddleLength/4) and (y > paddleY and y < (paddleY+paddleLength))

def isTouchingHost(paddleY, paddleLength, x, y, r):
    return (x+r) > (width-15-paddleLength/4) and (y > paddleY and y < (paddleY+paddleLength))

def getCollidingHostFace(x, y, paddleY, paddleLength):
    # this is a mess
    # The occasional +2 terms are simply to pad bottom and right edges, as those are not counted in the
    # collidepoint method. Removing the padding will cause the ball to phase through those edges
    rectWidth = paddleLength/4
    xL = width-15-rectWidth
    yT = paddleY
    yB = paddleY+paddleLength
    corner = ballRadius/3
    face = -1
    if pygame.Rect(xL, yT+corner, ballRadius*1.5+2, paddleLength-2*corner+2).collidepoint(x, y):
        face = LEFT_FACE
    elif pygame.Rect(xL+corner, yT, rectWidth-corner+2, corner+2).collidepoint(x, y):
        face = TOP_FACE
    elif pygame.Rect(xL, yT, corner+2, corner+2).collidepoint(x, y):
        if allowCornerCollisions:
            face = TL_CORNER
        else:
            face = LEFT_FACE
    elif pygame.Rect(xL+corner, yB-corner, rectWidth-corner+2, corner+2).collidepoint(x, y):
        face = BOTTOM_FACE
    elif pygame.Rect(xL, yB-corner, corner+2, corner+2).collidepoint(x, y):
        if allowCornerCollisions:
            face = BL_CORNER
        else:
            face = LEFT_FACE
    elif pygame.Rect(xL+ballRadius*1.5, yT+corner, rectWidth-ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = NO_FACE
    # print face
    return face

def getCollidingGuestFace(x, y, paddleY, paddleLength):
    # this is a mess
    # The +2 terms are simply to pad bottom and right edges, as those are not counted in the
    # collidepoint method. Removing the padding will cause the ball to phase through those edges
    rectWidth = paddleLength/4
    xL = 15
    xR = 15+rectWidth
    yT = paddleY
    yB = paddleY+paddleLength
    corner = ballRadius
    face = -1
    if pygame.Rect(xR-ballRadius*1.5, yT+corner, ballRadius*1.5+2, paddleLength-2*corner+2).collidepoint(x, y):
        face = RIGHT_FACE
    elif pygame.Rect(xL, yT, rectWidth-corner+2, corner+2).collidepoint(x, y):
        face = TOP_FACE
    elif pygame.Rect(xR-corner, yT, corner+2, corner+2).collidepoint(x, y):
        if allowCornerCollisions:
            face = TR_CORNER
        else:
            face = RIGHT_FACE
    elif pygame.Rect(xL, yB-corner, rectWidth-corner+2, corner+2).collidepoint(x, y):
        face = BOTTOM_FACE
    elif pygame.Rect(xR-corner, yB-corner, corner+2, corner+2).collidepoint(x, y):
        if allowCornerCollisions:
            face = BR_CORNER
        else:
            face = RIGHT_FACE
    elif pygame.Rect(xL, yT+corner, rectWidth-ballRadius*1.5, paddleLength-2*corner).collidepoint(x, y):
        face = NO_FACE
    # print face
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
                loadMusic(gameMusic)
                window = "Game"
            elif isInside(settingsButton):
                buttonPress.play()
                window = "Settings"
            elif isInside(quitButton):
                buttonPress.play()
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                window = "Game"
    return window, running

def processGameEvents(events):
    window = "Game"
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window = "Pause"
    return window

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
                buttonPress.play()
                window = "Game"
                pygame.time.wait(500)
            elif isInside(restartButton):
                buttonPress.play()
                loadMusic(gameMusic)
                window = "Game"
                shouldRestart = True
                pygame.time.wait(500)
            elif isInside(settingsButton):
                buttonPress.play()
                window = "Settings"
            elif isInside(quitButton):
                buttonPress.play()
                running = False
    return window, running, shouldRestart

def processWinEvents(events):
    window, running = "Win", True
    shouldRestart = False

    for event in events:
        if event.type == pygame.MOUSEBUTTONUP:
            if isInside(restartButton):
                buttonPress.play()
                loadMusic(gameMusic)
                window = "Game"
                shouldRestart = True
                pygame.time.wait(500)
            elif isInside(titleButton):
                buttonPress.play()
                loadMusic(titleMusic)
                window = "Title"
                shouldRestart = True
            elif isInside(quitButton):
                buttonPress.play()
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

def drawGuestHitboxes(x, y, paddleY, paddleLength):
    # draw the hitboxes - for testing
    rectWidth = paddleLength/4
    xL = 15
    xR = 15+rectWidth
    yT = paddleY
    yB = paddleY+paddleLength
    corner = ballRadius/3
    pygame.draw.rect(display, (255, 0, 0), (xR-ballRadius*1.5, yT+corner, ballRadius*1.5+2, paddleLength-2*corner+2), 2)
    pygame.draw.rect(display, (0, 255, 0), (xL, yT, rectWidth-corner+2, corner+2), 2)
    pygame.draw.rect(display, (0, 0, 255), (xR-corner, yT, corner+2, corner+2), 2)
    pygame.draw.rect(display, (255, 255, 0), (xL, yB-corner, rectWidth-corner+2, corner+2), 2)
    pygame.draw.rect(display, (0, 255, 255), (xR-corner, yB-corner, corner+2, corner+2), 2)
    pygame.draw.rect(display, (255, 0, 255), (xL, yT+corner, rectWidth-ballRadius*1.5, paddleLength-2*corner), 2)

def loadMusic(music):
    pygame.mixer.music.pause()
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)

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
checkmark = loadImageTransparent("checkmark.png")

pygame.display.set_caption("Despongcito 3: In Space (Deluxe Edition) (Collector's Edition)")
pygame.display.set_icon(gameLogo)

pastWindow = ""

hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()
# --- Main Loop --- #
loadMusic(titleMusic)

while running:
    if hostScore >= 7:
        display.blit(hostWinBackground, (0, 0))
        window = "Win"
    if guestScore >= 7:
        display.blit(guestWinBackground, (0, 0))
        window = "Win"

    if window == "Game":
        # Draw everything
        pygame.mixer.music.set_volume(1)

        pastWindow = "Game"
        display.blit(gameBackground, (0, 0))
        drawScoreboard(hostScore, guestScore)
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)

        ballX = ballX+ballVec.x
        ballY = ballY+ballVec.y

        # Check if the ball has hit a wall
        if ballY <= (0+ballRadius):
            hitSound.play()
            ballVec = ballVec.reflect(FACE_NORMALS[BOTTOM_FACE])
        elif ballY >= (height-ballRadius):
            hitSound.play()
            ballVec = ballVec.reflect(FACE_NORMALS[TOP_FACE])
        # Check if the ball has hit a paddle
        if invincibilityFrame == 0:
            if ballX < width/2:
                # guest
                collideX, collideY = closestPoint(ballX, ballY, ballRadius, 15, guestY, paddleLength/4, paddleLength)
                if distance(collideX, collideY, ballX, ballY) < ballRadius:
                    face = getCollidingGuestFace(collideX, collideY, guestY, paddleLength)
                    print face
                    if face > 0:
                        ballVec = ballVec.reflect(FACE_NORMALS[face])+guestVec
                        hitSound.play()
                        invincibilityFrame = 30
            else:
                # host
                collideX, collideY = closestPoint(ballX, ballY, ballRadius, width-15-paddleLength/4, hostY, paddleLength/4, paddleLength)
                if distance(collideX, collideY, ballX, ballY) < ballRadius:
                    face = getCollidingHostFace(collideX, collideY, hostY, paddleLength)
                    print face
                    if face > 0:
                        ballVec = ballVec.reflect(FACE_NORMALS[face])+hostVec
                        hitSound.play()
                        invincibilityFrame = 30
        else:
            invincibilityFrame = invincibilityFrame-1

        ballVec.scale_to_length(ballSpeed)

        # limit the angle to prevent it from getting too vertical
        if math.atan(abs(float(ballVec.y)/ballVec.x)) > math.radians(maxBallAngle):
            newVec = pygame.math.Vector2(ballSpeed*math.cos(math.radians(maxBallAngle))*math.copysign(1, ballVec.x), ballSpeed*math.sin(math.radians(maxBallAngle))*math.copysign(1, ballVec.y))
            ballVec = newVec

        # for testing
        if drawDebug:
            drawVector(ballVec, ballX, ballY)
            drawVector(guestVec, 15+paddleLength/8, guestY+paddleLength/2)
            drawVector(hostVec, width-15-paddleLength/8, hostY+paddleLength/2)
            drawGuestHitboxes(collideX, collideY, guestY, paddleLength)
            pygame.draw.line(display, BLACK, (ballX, ballY), (collideX, collideY), 2)
            pygame.draw.rect(display, (255, 255, 0), (collideX-2, collideY-2, 4, 4), 0)

        # Check if the ball has gone past a paddle
        if ballX+ballRadius < -10:
            ballX, ballY, ballVec = resetBall()
            hostScore = hostScore+1
            pointSound.play()
            pygame.time.wait(500)
        if ballX-ballRadius > width+10:
            ballX, ballY, ballVec = resetBall()
            guestScore = guestScore+1
            pointSound.play()
            pygame.time.wait(500)

        # Get the keyboard input
        keys = pygame.key.get_pressed()
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

        window = processGameEvents(pygame.event.get())

    elif window == "Pause":
        pygame.mixer.music.set_volume(0.5)
        display.blit(gameBackground, (0, 0))
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        resumeButton, restartButton, settingsButton, quitButton = drawPause()
        pastWindow = "Pause"

        window, running, shouldReset = processPauseEvents(pygame.event.get())
        if shouldReset:
            # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
            hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()

    elif window == "Win":
        pygame.mixer.music.set_volume(0.4)
        restartButton, titleButton, quitButton = drawWin(hostScore, guestScore)

        window, running, shouldReset = processWinEvents(pygame.event.get())
        if shouldReset:
            # This is ugly: should ask on monday if it is okay to use global statements to make this a lot easier
            hostScore, guestScore, ballX, ballY, ballVec, guestY, hostY, lastGuestY, lastHostY, guestSpeed, hostSpeed = resetGame()

    elif window == "Title":
        pygame.mixer.music.set_volume(1)
        display.blit(titleScreen, (0, 0))
        display.blit(*drawCenteredImage(width/2, height/2, despaSpider))
        display.blit(*drawCenteredImage(width/2, height/2, titleBarrier))
        display.blit(*drawCenteredImage(width/2, height/2.5, titleText))
        playButton, settingsButton, quitButton = drawTitle()
        pastWindow = "Title"

        window, running = processTitleEvents(pygame.event.get())

    elif window == "Settings":
        pygame.mixer.music.set_volume(0.4)
        display.blit(settingScreen, (0, 0))
        drawGame(guestY, hostY, paddleLength, ballX, ballY, ballRadius)
        radiusSlider, paddleSlider, speedSlider, backButton, resetRadius, resetLength, resetSpeed, paddleModeButton, cornerCheckbox, debugCheckbox, angleSlider, resetAngle = drawSettings(radiusOffset, paddleOffset, speedOffset, paddleMode, allowCornerCollisions, drawDebug, angleOffset)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    window = pastWindow
            elif event.type == pygame.MOUSEMOTION:
                if (isInside(radiusSlider) or sliderInFocus[RADIUS]) and event.buttons[0] == 1:
                    sliderInFocus[RADIUS] = True
                    pygame.mouse.set_visible(False)
                    radiusOffset = constrainValue(radiusOffset+event.rel[0], 0, 100)
                    ballRadius = offsetToValue(radiusOffset, radiusRange)
                elif (isInside(paddleSlider) or sliderInFocus[PADDLE]) and event.buttons[0] == 1:
                    sliderInFocus[PADDLE] = True
                    pygame.mouse.set_visible(False)
                    paddleOffset = constrainValue(paddleOffset+event.rel[0], 0, 100)
                    paddleLength = offsetToValue(paddleOffset, paddleRange)
                elif (isInside(speedSlider) or sliderInFocus[SPEED]) and event.buttons[0] == 1:
                    sliderInFocus[SPEED] = True
                    pygame.mouse.set_visible(False)
                    speedOffset = constrainValue(speedOffset+event.rel[0], 0, 100)
                    ballSpeed = offsetToValue(speedOffset, speedRange)
                elif (isInside(angleSlider) or sliderInFocus[ANGLE]) and event.buttons[0] == 1:
                    sliderInFocus[ANGLE] = True
                    pygame.mouse.set_visible(False)
                    angleOffset = constrainValue(angleOffset+event.rel[0], 0, 100)
                    maxBallAngle = offsetToValue(angleOffset, angleRange)
            elif event.type == pygame.MOUSEBUTTONUP:
                pygame.mouse.set_visible(True)  # Make the mouse visible once the mouse has clicked off any slider
                for i in range(len(sliderInFocus)):
                    sliderInFocus[i] = False
                buttonPress.play()
                if isInside(backButton):
                    window = pastWindow
                elif isInside(resetRadius):
                    ballRadius = DEFAULT_RADIUS
                    radiusOffset = calculateOffset(ballRadius, radiusRange)
                elif isInside(resetLength):
                    paddleLength = DEFAULT_LENGTH
                    lengthOffset = calculateOffset(paddleLength, paddleRange)
                elif isInside(resetSpeed):
                    ballSpeed = DEFAULT_SPEED
                    speedOffset = calculateOffset(ballSpeed, speedRange)
                elif isInside(paddleModeButton):
                    paddleMode = getNewpaddleMode(paddleMode)
                elif isInside(cornerCheckbox):
                    allowCornerCollisions = not allowCornerCollisions
                elif isInside(debugCheckbox):
                    drawDebug = not drawDebug

    clock.tick(100)
    pygame.display.update()
# ---------------- #
pygame.quit()
