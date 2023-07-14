import sys
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN, Rect

pygame.init()
SURFACE = pygame.display.set_mode((900, 600))
FPSCLOCK = pygame.time.Clock()

FOODS = [] #エサの座標を格納した配列
SNAKE = [] #ヘビの座標を格納した配列
(W, H) = (30, 20) #画面の幅と高さ

#ランダムな場所にエサを配置する関数
def add_food():
    while True:
        #ランダムな座標を生成
        pos = (random.randint(0, W-1), random.randint(0, H-1))
        #エサやヘビがすでにある場合、乱数を再生成
        if pos in FOODS or pos in SNAKE:
            continue
        FOODS.append(pos)
        break

#エサを別の場所へ移動する関数
def move_food(pos):
    i = FOODS.index(pos)
    del FOODS[i]
    add_food()

#画面を描画する関数
def paint(message):
    SURFACE.fill((0, 0, 0))
    #エサを描画
    for food in FOODS:
        pygame.draw.ellipse(SURFACE, (0, 255, 0), Rect(food[0]*30, food[1]*30, 30, 30))
    #ヘビを描画
    for body in SNAKE:
        pygame.draw.rect(SURFACE, (0, 255, 255), Rect(body[0]*30, body[1]*30, 30, 30))
    #盤の線を描画
    for index in range(30):
        pygame.draw.line(SURFACE, (64, 64, 64), (index*30, 0), (index*30, 600))
    for index in range(20):
        pygame.draw.line(SURFACE, (64, 64, 64), (0, index*30), (900, index*30))
    #ゲームオーバーのメッセージを描画
    if message != None:
        SURFACE.blit(message, (300, 300))
    pygame.display.update()

def main():
    myfont = pygame.font.SysFont(None, 80)
    key = K_DOWN
    message = None
    game_over = False
    #ヘビの初期座標
    SNAKE.append((int(W/2), int(H/2)))
    #エサを10個配置
    for _ in range(10):
        add_food()

    while True:
        for event in pygame.event.get():
            #ゲーム終了
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                key = event.key

        if not game_over:
            #キーの入力に応じて次のヘビの頭の位置を決定
            if key == K_LEFT:
                head = (SNAKE[0][0] - 1, SNAKE[0][1])
            elif key == K_RIGHT:
                head = (SNAKE[0][0] + 1, SNAKE[0][1])
            elif key == K_UP:
                head = (SNAKE[0][0], SNAKE[0][1] - 1)
            elif key == K_DOWN:
                head = (SNAKE[0][0], SNAKE[0][1] + 1)

            #自分自身、左右の壁、上下の壁への衝突判定
            if head in SNAKE or head[0] < 0 or head[0] >= W or head[1] < 0 or head[1] >= H:
                message = myfont.render("Game Over!", True, (255, 255, 0))
                game_over = True

            #ヘビの移動
            SNAKE.insert(0, head)
            #エサがある場合はエサを移動
            if head in FOODS:
                move_food(head)
            #エサがない場合はヘビの尻尾を削除
            else:
                SNAKE.pop()

        paint(message)
        FPSCLOCK.tick(5)

if __name__ == '__main__':
    main()
