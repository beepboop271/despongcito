
width = 800
height = 600

guestY = height/2
hostY = height/2

WHITE = (255,255,255)
BLACK = (0,0,0)

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((width, height))

guestUp = pygame.K_w
guestDown = pygame.K_s
hostUp = pygame.K_i
hostDown = pygame.K_k
ballRadius = 

dy = 2

window = "Title"
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window = "Pause"
    
    display.fill(BLACK)
    if window == "Game":
        drawGame()
    elif window == "Pause":
        drawPause()
    elif window == "Title":
        drawTitle()
    clock.tick(120)

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
