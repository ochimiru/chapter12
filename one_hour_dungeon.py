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
        y = random.randint(3, DUNGEON_H-4)
        if dungeon[y][x] == 0:
            dungeon[y][x] = random.choice([1, 2, 2, 2, 2)]

    # プレイヤーの初期位置
    while True:
        pl_x = random.randint(3, DUNGEON_W-4)
        pl_y = random.randint(3, DUNGEON_H-4)
        if dungeon[pl_y][pl_x] == 0:
            break
    
    pl_d = 1
    pl_a = 2

# 主人公の移動
def move_player(key):
    global idx, tmr, pl_x, pl_y, pl_d, pl_a, pl_life, food, potion, blazegem, treasure

    if dungeon[pl_y][pl_x] == 1 #宝箱に乗った
        dungeon[pl_y][pl_x] = 0
        treasure = random.choice([0,0,0,1,1,1,1,1,1,2])
        if treasure = 0:
            potion += 1
        if treasure = 1:
            blazegem += 1
        if treasure = 2:
            food = int(food/2)
        idx = 3
        tmr = 0
        return
    if dungeon[pl_y][pl_x] == 2: # 繭に乗った
        dungeon[pl_y][pl_x] = 0
        r = random.randint(0, 99)
        if r < 40: # 食料
            treasure = random.choice([3,3,3,4])
            if treasure == 3:
                food += 20
            if treasure == 4:
                food += 100
            idx = 3
            tmr = 0
        else: # 敵出現
            idx = 10
            tmr = 0
        return
    if dungeon[pl_y][pl_x] == 3: # 階段に乗った
        idx = 2
        tmr = 0
        return

    # 方向キーで上下左右に移動
    x = pl_x
    y = pl_y
    if key[K_UP] == 1:
        pl_d = 0
        if dungeon[pl_y-1][pl_x] != 9:
            pl_y -= 1
    if key[K_DOWN] == 1:
        pl_d = 1
        if dungeon[pl_y+1][pl_x] != 9:
            pl_y += 1
    if key[K_LEFT] == 1:
        pl_d = 2
        if dungeon[pl_y][pl_x-1] != 9:
            pl_x -= 1
    if key[K_RIGHT] == 1:
        pl_d = 3
        if dungeon[pl_y][pl_x+1] != 9:
            pl_x += 1
    pl_a = pl_d * 2
    if pl_x != x or pl_y != y: # 移動したら食料の量と体力を計算
        pl_a += tmr%2
        if food > 0:
            food -= 1
            if pl_life < pl_lifemax:
                pl_life += 1
        else:
            pl_life -= 5
            if pl_life <= 0:
                pl_life = 0
                pygame.mixer.music.stop()
                idx = 9
                tmr = 0

# 影付き文字の表示
def draw_text(bg, txt, x, y, fnt, col):
    sur = fnt.render(txt, True, BLACK)
    bg.blit(sur, [x+1, y+2])
    sur = fnt.render(txt, True, col)
    bg.blit(sur, [x, y])

# 主人公の能力を表示
def draw_para(bg, fnt):
    X = 30
    Y = 600
    bg.blit(imgPara, [X, Y])
    col = WHITE
    if pl_life < 10 and tmr%2 == 0:
        col = RED
    draw_text(bg, " {}/{}".format(pl_life, pl_lifemax), X+128, Y+6, fnt, col)
    draw_text(bg, str(pl_str), X+128, Y+33, fnt, WHITE)
    col = WHITE
    if food == 0 and tmr%w == 0:
        col = RED
    draw_text(bg, str(food), X+128, Y+60, fnt, col)
    draw_text(bg, str(potion), X+266, Y+6, fnt, WHITE)
    draw_text(bg, str(blazegem), X+266, Y+ 33, fnt, WHITE)

# 戦闘に入る準備をする
def init_battle():
    global imgEnemy, emy_name, emy_lifemax, emy_life, emy_str, emy_x, emy_y
    typ = random.randint(0, floor)
    if floor >= 10:
        typ = random.randint(0, 9)
    lev = random.randint(1, floor)
    imgEnemy = pygame.image.load("image/enemy" + str(typ) + ".png")
    emy_name = EMY_NAME[typ] + "LV" + str(lev)
    emy_lifemax = 60*(typ+1) + (lev-1)*10
    emy_life = emy_lifemax
    emy_str = int(emy_lifemax/8)
    emy_x = 440-imgEnemy.get_width()/2
    emy_y = 560-imgEnemy.get_height()

# 敵の体力を表示するバー
def draw_bar(bg, x, y, w, h, val, ma):
    pygame.draw.rect(bg, WHITE, [x-2, y-2, w+4, h+4])
    pygame.draw.rect(bg, BLACK, [x, y, w, h])
    if val > 0:
        pygame.draw.rect(bg, (0, 128, 255), [x, y, w*val/ma, h])

# 戦闘画面の描写
def draw_battle(bg, fnt):
    global emy_blink, dmg_eff
    bx = 0
    by = 0
    if dmg_eff > 0:
        dmg_eff -= 1
        bx = random.randint(-20, 20)
        by = random.randint(-10, 10)
    bg.blit(imgBtlBG, [bx, by])
    if emy_life > 0 and emy_blink%2 == 0:
        bg.blit(imgEnemy, [emy_x, emy_y+emy_step])
    draw_bar(bg, 340, 580, 200, 10, emy_life, emy_lifemax)
    if emy_blink > 0:
        emy_blink -= 1
    for i in range(10): # 戦闘メッセージの表示
        draw_text(bg, message[i], 600, 100+i*50, fnt, WHITE)
        draw_para(bg, fnt) # 主人公の能力を表示

# コマンドの入力と表示
