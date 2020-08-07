import pygame
import os
import random
from pygame import mixer

pygame.init()

W, H = 1400, 787
win = pygame.display.set_mode((W, H))
pygame.display.set_caption('Ninja Game')

backgrounds = [pygame.image.load(os.path.join('backgrounds', 'bg' + str(x) + '.png')) for x in range(1, 5)]
grounds = [pygame.image.load(os.path.join('backgrounds', 'ground' + str(x) + '.png')) for x in range(1, 5)]
ground = grounds[0]
scoreboard = pygame.image.load('board.png')

mixer.music.load('BlazerRail.mp3')
mixer.music.play(-1)

jumpSound = mixer.Sound('jump.wav')
landSound = mixer.Sound('landing.wav')
smashSound = mixer.Sound('smash.wav')
splatSound = mixer.Sound('splat.wav')

bg = backgrounds[0]
bgX = 0
bgX2 = bg.get_width()

mute = False

clock = pygame.time.Clock()


class Player(object):
    run = [pygame.image.load(os.path.join('running', 'Run__00' + str(x) + '.png')) for x in range(0, 10)]
    jump = [pygame.image.load(os.path.join('jumping', 'Jump__00' + str(x) + '.png')) for x in range(0, 10)]
    glide = pygame.image.load('Glide__000.png')
    slide = pygame.image.load('Slide__000.png')
    die = [pygame.image.load(os.path.join('dying', 'Dead__00' + str(x) + '.png')) for x in range(0, 10)]
    climb = [pygame.image.load(os.path.join('climbing', 'Climb_00' + str(x) + '.png')) for x in range(0, 10)]

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.running = True
        self.jumping = False
        self.gliding = False
        self.landing = False  # landing after gliding
        self.sliding = False
        self.climbing = False
        self.dying = False
        self.runCount = 0
        self.jumpCount = 15
        self.climbCount = 0
        self.dieCount = 0
        self.hitBox = (self.x + 25, self.y + 5, self.width - 37, self.height - 35)

    def draw(self, screen):
        if self.running:
            if self.runCount > 29:
                self.runCount = 0
            screen.blit(self.run[self.runCount // 3], (self.x, self.y))
            self.runCount += 2
            self.hitBox = (self.x + 25, self.y + 5, self.width - 37, self.height - 35)
        elif self.jumping:
            # this is because of lag
            if self.jumpCount == -13 and not mute:
                landSound.play()
            if self.jumpCount >= -15:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                self.y -= self.jumpCount ** 2 * 0.4 * neg
                self.jumpCount -= 1
            else:
                self.jumping = False
                self.jumpCount = 15
                self.running = True
                self.runCount = 0
            self.hitBox = (self.x + 25, self.y + 15, self.width - 50, self.height - 40)
            screen.blit(self.jump[int((self.jumpCount - 14) * 0.99 // -3)], (self.x, self.y))
        elif self.gliding:
            if self.y + 3 < 629:
                self.y += 3
            else:
                self.y = 629
                self.gliding = False
                self.running = True
                self.jumpCount = 15
            self.hitBox = (self.x + 35, self.y + 15, self.width - 30, self.height - 50)
            screen.blit(self.glide, (self.x, self.y))
        elif self.landing:
            # this is because of lag
            if 579 < self.y < 595 and not mute:
                landSound.play()
            if self.y + 16 < 629:
                self.y += 16
            else:
                self.y = 629
                self.landing = False
                self.running = True
                self.jumpCount = 15
            self.hitBox = (self.x + 25, self.y + 13, self.width - 50, self.height - 30)
            screen.blit(self.jump[4], (self.x, self.y))
        elif self.sliding:
            self.hitBox = (self.x + 10, self.y + 30, self.width - 40, self.height - 30)
            screen.blit(self.slide, (self.x, self.y + 20))
        elif self.climbing:
            if self.climbCount > 29:
                self.climbCount = 0
            screen.blit(self.climb[self.climbCount // 3], (self.x, self.y))
            self.climbCount += 2
        elif self.dying:
            if self.y + (self.dieCount // 3) ** 2 * 0.3 < 600:
                self.y += (self.dieCount // 3) ** 2 * 0.3
            else:
                self.y = 603
            if self.dieCount > 39:
                self.dieCount = 39
            if self.y < 603:
                screen.blit(self.die[0], (self.x, self.y))
            else:
                screen.blit(self.die[self.dieCount // 4], (self.x, self.y))
            self.dieCount += 1
        # pygame.draw.rect(screen, (255, 0, 0), self.hitBox, 2)


class Spikes(object):
    spikes = [pygame.image.load(os.path.join('obstacles', 'spikes_' + str(x) + '.png')) for x in range(1, 3)]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        s = random.randrange(0, 2)
        if s == 0:
            self.width = 128
            self.spike = self.spikes[0]
        else:
            self.width = 147
            self.spike = self.spikes[1]
        self.height = 76
        self.hitBox = (self.x + 10, self.y + 15, self.width - 20, self.height)

    def draw(self, screen):
        screen.blit(self.spike, (self.x, self.y))
        self.hitBox = (self.x + 10, self.y + 15, self.width - 20, self.height)
        # pygame.draw.rect(screen, (255, 0, 0), self.hitBox, 2)

    def collide(self, rect):
        if rect[0] + rect[2] > self.hitBox[0] and rect[0] < self.hitBox[0] + self.hitBox[2]:
            if rect[1] + rect[3] > self.hitBox[1] and rect[1] < self.hitBox[1] + self.hitBox[3]:
                return True
        return False


class Blade(object):
    rope = [pygame.image.load(os.path.join('obstacles', 'rope.png'))][0]
    blade = [pygame.image.load(os.path.join('obstacles', 'blade.png'))][0]
    spike = [pygame.image.load(os.path.join('obstacles', 'spike.png'))][0]
    attachment = blade

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        s = random.randrange(0, 2)
        if s == 0:
            self.attachment = self.blade
            self.height = height
        else:
            self.attachment = self.spike
            self.height = height + 83
        self.width = width
        if s == 0:
            self.hitBox = (self.x + 20, self.y + 610, self.width - 40, self.height - 520)
        else:
            self.hitBox = (self.x + 20, self.y + 700, self.width - 40, self.height - 600)

    def draw(self, screen):
        screen.blit(self.attachment, (self.x, self.y + 530))
        screen.blit(self.rope, (self.x + 87, self.y - 45))

        if self.attachment == self.blade:
            self.hitBox = (self.x + 20, self.y + 610, self.width - 40, self.height - 520)
        else:
            self.hitBox = (self.x + 20, self.y + 700, self.width - 40, self.height - 600)

        # pygame.draw.rect(screen, (255, 0, 0), self.hitBox, 2)

    def collide(self, rect):
        if rect[0] + rect[2] > self.hitBox[0] and rect[0] < self.hitBox[0] + self.hitBox[2]:
            if rect[1] + rect[3] > self.hitBox[1] and rect[1] < self.hitBox[1] + self.hitBox[3]:
                return True
        return False


class Post(object):
    post = pygame.image.load('large_post.png')

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        screen.blit(self.post, (self.x, self.y))


def update_file():
    global score
    f = open('scores.txt', 'r')
    file = f.readlines()
    last = int(file[0])

    if last < int(score):
        f.close()
        file = open('scores.txt', 'w')
        file.write(str(score))
        file.close()

        return score

    return last


def title_screen():
    global bg, ground, bgX, bgX2, runner, run, mute
    rope = [pygame.image.load(os.path.join('obstacles', 'rope.png'))][0]
    title = pygame.image.load('title.png')
    running = True
    runner.running = True
    game_start = False
    y_title = 200
    y_ropes = -300
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                game_start = True

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    if mute:
                        mute = False
                        mixer.music.play(-1)
                    else:
                        mute = True
                        mixer.music.pause()

        bgX -= SPEED
        bgX2 -= SPEED
        if bgX < bg.get_width() * -1:
            bgX = bg.get_width()
        if bgX2 < bg.get_width() * -1:
            bgX2 = bg.get_width()

        if game_start:
            y_title -= 20
            y_ropes -= 20
            if y_title + 300 < 0:
                running = False

        clock.tick(40)
        win.blit(bg, (bgX, 0))
        win.blit(bg, (bgX2, 0))
        runner.draw(win)

        win.blit(scoreboard, (1200, 10))
        font = pygame.font.SysFont('monospace', 40)
        text = font.render('Score: ' + str(score), 1, (0, 0, 0))
        win.blit(text, (1237, 47))

        win.blit(ground, (bgX, 0))
        win.blit(ground, (bgX2, 0))
        win.blit(title, (W / 2 - title.get_width() / 2 + 5, y_title))
        win.blit(rope, (400, y_ropes))
        win.blit(rope, (980, y_ropes))
        pygame.display.update()

    run = True


def end_screen():
    end_title = pygame.image.load('post.png')
    rope = [pygame.image.load(os.path.join('obstacles', 'rope.png'))][0]
    global score, bg, ground, bgX, bgX2, runner, obstacles, posts, SPEED, isekai, game_over, game_over_count, run, mute
    running = True
    while running:
        pygame.time.delay(100)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    if mute:
                        mute = False
                        mixer.music.play(-1)
                    else:
                        mute = True
                        mixer.music.pause()
        redraw_window()
        win.blit(end_title, (W / 2 - end_title.get_width() / 2 + 5, 200))
        win.blit(rope, (350, -320))
        win.blit(rope, (1020, -320))
        large_font = pygame.font.SysFont('monospace', 80)
        highscore = large_font.render('Highscore: ' + str(update_file()), 1, (0, 0, 0))
        win.blit(highscore, (W/2 - highscore.get_width()/2, 323))
        new_score = large_font.render('Score: ' + str(score), 1, (0, 0, 0))
        win.blit(new_score, (W / 2 - new_score.get_width() / 2, 397))
        pygame.display.update()

    bg = backgrounds[0]
    ground = grounds[0]
    mixer.music.load('BlazerRail.mp3')
    mixer.music.play(-1)
    if mute:
        mixer.music.pause()
    bgX = 0
    bgX2 = bg.get_width()
    runner = Player(160, 629, 100, 126)
    obstacles = []
    posts = []
    SPEED = 8
    score = 0
    isekai = False
    game_over = False
    game_over_count = 146
    run = True


def redraw_window():
    win.blit(bg, (bgX, 0))
    win.blit(bg, (bgX2, 0))
    for p in posts:
        p.draw(win)
    if not isekai:
        for obs in obstacles:
            obs.draw(win)
        runner.draw(win)
    else:
        runner.draw(win)
        for obs in obstacles:
            obs.draw(win)

    win.blit(scoreboard, (1200, 10))
    font = pygame.font.SysFont('monospace', 40)
    text = font.render('Score: ' + str(score), 1, (0, 0, 0))
    win.blit(text, (1237, 47))

    win.blit(ground, (bgX, 0))
    win.blit(ground, (bgX2, 0))
    pygame.display.update()


runner = Player(160, 629, 100, 126)
obstacles = []
posts = []
SPEED = 8
score = 0
isekai = False
game_over = False
game_over_count = 146
run = False
title_screen()
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            quit()

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     mixer.music.load('BlazerRail.mp3')
        #     mixer.music.play(-1)
        #     if mute:
        #         mixer.music.pause()
        #     bg = backgrounds[0]
        #     ground = grounds[0]
        #     bgX = 0
        #     bgX2 = bg.get_width()
        #     runner = Player(160, 629, 100, 126)
        #     obstacles = []
        #     posts = []
        #     SPEED = 8
        #     score = 0
        #     isekai = False
        #     game_over = False
        #     game_over_count = 146
        #     run = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if mute:
                    mute = False
                    mixer.music.play(-1)
                else:
                    mute = True
                    mixer.music.pause()

    if isekai:
        if runner.y < -1 * (runner.height + 5):
            runner.y = 800
            posts = [Post(160, 650, 80, 837)]
            bgX = 0
            bgX2 = bg.get_width()
            if bg == backgrounds[0]:
                bg = backgrounds[1]
                ground = grounds[1]
                mixer.music.load('AfricanSafari.mp3')
                mixer.music.play(-1)
            elif bg == backgrounds[1]:
                bg = backgrounds[2]
                ground = grounds[2]
                mixer.music.load('B-3.mp3')
                mixer.music.play(-1)
            elif bg == backgrounds[2]:
                bg = backgrounds[3]
                ground = grounds[3]
                mixer.music.load('YoungLove.mp3')
                mixer.music.play(-1)
            else:
                bg = backgrounds[0]
                ground = grounds[0]
                mixer.music.load('BlazerRail.mp3')
                mixer.music.play(-1)
            if mute:
                mixer.music.pause()
            obstacles = []
        elif runner.y <= 629 and posts[0].y == 650:
            runner.y = 629
            runner.climbing = False
            runner.running = True
            runner.jumpCount = 15
            runner.climbCount = 0
            runner.runCount = 0
            isekai = False
        else:
            runner.y -= 6
    else:

        for obstacle in obstacles:
            obstacle.x -= SPEED
            if obstacle.collide(runner.hitBox) and not game_over:
                if isinstance(obstacle, Spikes) and not mute:
                    splatSound.play()
                elif isinstance(obstacle, Blade) and not mute:
                    smashSound.play()
                game_over = True
                runner.dying = True
                runner.running = False
                runner.jumping = False
                runner.gliding = False
                runner.sliding = False
                runner.landing = False
            if obstacle.x < obstacle.width * -1:
                obstacles.pop(obstacles.index(obstacle))
        for p in posts:
            p.x -= SPEED
            if p.x < p.width * -1:
                posts.pop(posts.index(p))

        if game_over:
            SPEED = game_over_count // 18
            if game_over_count - 1 < 0:
                game_over_count = 0
                end_screen()
            else:
                game_over_count -= 1

        bgX -= SPEED
        bgX2 -= SPEED
        if bgX < bg.get_width() * -1:
            bgX = bg.get_width()
        if bgX2 < bg.get_width() * -1:
            bgX2 = bg.get_width()

        randNum = random.randrange(0, 1000)
        if randNum < 17:
            score += 1
            num = random.randrange(0, 2)
            if num == 0:
                obstacles.append(Spikes(W, 660))
            elif num == 1:
                num2 = random.randrange(-230, 0)
                blade = Blade(W, num2, 200, 575)
                obstacles.append(blade)

        keys = pygame.key.get_pressed()

        if not game_over:
            if runner.gliding and not keys[pygame.K_UP]:
                runner.gliding = False
                runner.landing = True
            elif runner.sliding and not keys[pygame.K_DOWN]:
                runner.slideCount = 0
                runner.sliding = False
                runner.running = True
            elif keys[pygame.K_UP]:
                if not (runner.jumping or runner.gliding or runner.landing):
                    if not mute:
                        jumpSound.play()
                runner.jumping = True
                runner.running = False
                if runner.jumpCount <= 0:
                    runner.jumping = False
                    runner.gliding = True
            elif keys[pygame.K_DOWN] and not (runner.jumping or runner.landing or runner.gliding):
                runner.running = False
                runner.sliding = True

            if len(posts) == 0 and score % 20 == 0 and score > 0:
                posts.append(Post(W, -50, 80, 837))

            if len(posts) > 0 and posts[0].y == -50 and runner.x >= posts[0].x - 5 and not runner.dying:
                isekai = True
                runner.climbing = True
                runner.running = False
                runner.jumping = False
                runner.gliding = False
                runner.sliding = False
                runner.landing = False

    clock.tick(40)
    redraw_window()
