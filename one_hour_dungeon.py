import pygame
import sys
import random
from pygame.locals import *

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 255, 255)
CYAN = (0, 255, 255)
BLINK = [
        (224, 255, 255),
        (192, 240, 255),
        (128, 224, 255),
        (64, 192, 255),
        (128, 224, 255),
        (192, 240, 255)
        ]

# 画像の読み込み
imgTitle = pygame.image.load("image/title.png")
imgWall = pygame.image.load("image/wall.png")
imgWall2 = pygame.image.load("image/wall2.png")
imgDark = pygame.image.load("image/dark.png")
imgPara = pygame.image.load("image/parameter.png")
imgBtlBG = pygame.image.load("image/btlbg.png")
imgEnemy = pygame.image.load("image/enemy0.png")
imgItem = [
        pygame.image.load("image/potion.png"),
        pygame.image.load("image/blaze_gem.png"),
        pygame.image.load("image/spoiled.png"),
        pygame.image.load("image/apple.png"),
        pygame.image.load("image/meat.png")
        ]
imgFloor = [
        pygame.image.load("image/floor.png"),
        pygame.image.load("image/tbox.png"),
        pygame.image.load("image/cocoon.png"),
        pygame.image.load("image/stairs.png")
        ]
imgPlayer = []
for i in range(9):
    imgPlayer.append("image/mychar" + str(i) + ".png")
imgEffect = [
        pygame.image.load("image/effect_a.png")
        pygame.image.load("image/effect_b.png")
        ]

# 変数の宣言
speed = 1
idx = 0
tmr = 0
floor = 0
fl_max = 1
welcome = 0

pl_x = 0
pl_y = 0
pl_d = 0
pl_a = 0
pl_lifemax = 0
pl_life = 0
pl_str = 0
food = 0
potion = 0
blazegem = 0
treasure = 0

emy_name = ""
emy_lifemax = 0
emy_life = 0
emy_str = 0
emy_x = 0
emy_y = 0
emy_step = 0
emy_blink = 0

dmg_eff = 0
btl_cmd = 0

COMMAND = ["[A]ttack", "[P]otion", "[B]laze gem", "[R]un"]
THE_NAME = ["Potion", "Blaze gem", "Food spoiled", "Food +20", "Food +100"]
EMY_NAME = ["Green slime", "Red slime", "Axe beast", "Ogre", "Sword man",
            "Death hornet", "Signal slime", "Devil plant", "Twin killer", "Hell"]

MAZE_W = 11
MAZE_H = 9
maze = []
for y in range(MAZE_H):
    maze.append([0] * MAZE_W)

DUNGEON_W = MAZE_W * 3
DUNGEON_H = MAZE_H * 3
dungeon = []
for y in range(DUNGEON_H):
    dugeon.append([0] * DUNGEON_W)

# ダンジョンの自動生成
def make_dungeon():
    XP = [0, 1, 0, -1]
    YP = [-1, 0, 1, 0]
    # 周りの壁
    for x in range(MAZE_W):
        maze[0][x] = 1
        maze[MAZE_H-1][x] = 1
    for y in range(MAZE_H):
        maze[y][0] = 1
        maze[y][MAZE_W-1] = 1
    # 中を何もない状態に
    for y in range(1, MAZE_H-1):
        for x in range(1, MAZE_W-1):
            maze[y][x] = 0
    # 柱
    for y in range(2, MAZE_H-2, 2):
        for x in range(2, MAZE_W-2, 2):
            maze[y][x] = 1
    # 柱から上下左右に壁を作る
    for y in range(2, MAZE_H-2, 2):
        for x in range(2, MAZE_W-2, 2):
            d = random.randint(0, 3)
            if x > 2:    #二列目からは左に壁を作らない
                d = random.randint(0, 2)
            maze[y+YP[d]][x+XP[d]] = 1

    # 迷路からダンジョンを作る
    # 全体を壁にする
    for y in range(DUNGEON_H):
        for x in range(DUNGEON_W):
            dungeon[y][x] = 9
    # 部屋と通路の配置
    for y in range(1, MAZE_H-1):
        for x in range(1, MAZE_W-1):
            dx = x * 3 + 1
            dy = y * 3 + 1
            if maze[y][x] == 0:
                if random.randint(0, 99) < 20: # 部屋を作る
                    for ry in range(-1, 2):
                        for rx in range(-1, 2):
                            dungeon[dy+ry][dx+rx] = 0
                else:
                    dungeon[dy][dx] = 0
                    if maze[y-1][x] == 0: dungeon[dy-1][dx] = 0
                    if maze[y+1][x] == 0: dungeon[dy+1][dx] = 0
                    if maze[y][x-1] == 0: dungeon[dy][dx-1] = 0
                    if maze[y][x+1] == 0: dungeon[dy][dx+1] = 0

# ダンジョンを描写する
def draw_dungeon(bg, fnt):
    bg.fill(BLACK)
    for y in range(-4, 6):
        for x in range(-5, 6):
            X = (x+5) * 80
            Y = (y+4) * 80
            dx = pl_x + x
            dy = pl_y + y
            if 0 <= dx and dx < DUNGEON_W and 0 <= dy and < DUNGEON_H:
                if dungeon[dy][dx] <= 3:
                    bg.blit(imgFloor[dungeon[dy][dx], [X, Y])
                if dungeon[dy][dx] == 9:
                    bg.blit(imgWall, [X, Y-40])
                    if dy >= 1 and dungeon[dy-1][dx] == 9:
                        bg.blit(imgWall2, [X, Y-80])
            if x == 0 and y == 0:   # 主人公キャラの表示
                bg.blit(imgPlayer[pl_a], [X, Y-40])
    bg.blit(imgDark, [0, 0])    # 四隅が暗闇の画像を重ねる
    draw_para(bg, fnt)  # 主人公の能力を表示

# 床にイベントを配置する
def put_event():
    global pl_x, pl_y, pl_d, pl_a
    # 階段の配置
    while True:
        x = random.randint(3, DUNGEON_W-4)
        y = random.randint(3, DUNGEON_H-4)
        if dungeon[y][x] == 0:
            for ry in range(-1, 2):
                for rx in range(-1, 2):
                    dungeon[y+ry][x+rx] = 0
            dungeon[y][x] = 3
            break

    # 宝箱と繭の配置
    for i in range(60):
        x = random.randint(3, DUNGEON_W-4)

#-------------------184行目まで----------------------------

