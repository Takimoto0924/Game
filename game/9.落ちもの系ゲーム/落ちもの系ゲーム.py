import sys
from math import sqrt
from random import randint
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_DOWN, K_SPACE

BLOCK_DATA = (
    (
        (0, 0, 1, \
         1, 1, 1, \
         0, 0, 0),
        (0, 1, 0, \
         0, 1, 0, \
         0, 1, 1),
        (0, 0, 0, \
         1, 1, 1, \
         1, 0, 0),
        (1, 1, 0, \
         0, 1, 0, \
         0, 1, 0),
    ), (
        (2, 0, 0, \
         2, 2, 2, \
         0, 0, 0),
        (0, 2, 2, \
         0, 2, 0, \
         0, 2, 0),
        (0, 0, 0, \
         2, 2, 2, \
         0, 0, 2),
        (0, 2, 0, \
         0, 2, 0, \
         2, 2, 0)
    ), (
        (0, 3, 0, \
         3, 3, 3, \
         0, 0, 0),
        (0, 3, 0, \
         0, 3, 3, \
         0, 3, 0),
        (0, 0, 0, \
         3, 3, 3, \
         0, 3, 0),
        (0, 3, 0, \
         3, 3, 0, \
         0, 3, 0)
    ), (
        (4, 4, 0, \
         0, 4, 4, \
         0, 0, 0),
        (0, 0, 4, \
         0, 4, 4, \
         0, 4, 0),
        (0, 0, 0, \
         4, 4, 0, \
         0, 4, 4),
        (0, 4, 0, \
         4, 4, 0, \
         4, 0, 0)
    ), (
        (0, 5, 5, \
         5, 5, 0, \
         0, 0, 0),
        (0, 5, 0, \
         0, 5, 5, \
         0, 0, 5),
        (0, 0, 0, \
         0, 5, 5, \
         5, 5, 0),
        (5, 0, 0, \
         5, 5, 0, \
         0, 5, 0)
    ), (
        (6, 6, 6, 6),
        (6, 6, 6, 6),
        (6, 6, 6, 6),
        (6, 6, 6, 6)
    ), (
        (0, 7, 0, 0, \
         0, 7, 0, 0, \
         0, 7, 0, 0, \
         0, 7, 0, 0),
        (0, 0, 0, 0, \
         7, 7, 7, 7, \
         0, 0, 0, 0, \
         0, 0, 0, 0),
        (0, 0, 7, 0, \
         0, 0, 7, 0, \
         0, 0, 7, 0, \
         0, 0, 7, 0),
        (0, 0, 0, 0, \
         0, 0, 0, 0, \
         7, 7, 7, 7, \
         0, 0, 0, 0)
    )
)

#ブロックオブジェクト
class Block:
    def __init__(self, count):
        self.turn = randint(0, 3) #ブロックの向き
        self.type = BLOCK_DATA[randint(0, 6)] #ブロックの2次元データ
        self.data = self.type[self.turn] #ブロックの1次元データ
        self.size = int(sqrt(len(self.data))) #ブロックのサイズ
        self.xpos = randint(2, 8 - self.size) #ブロックのx座標
        self.ypos = 1 - self.size #ブロックのy座標
        self.fire = count + INTERVAL #落下開始時刻

    #ブロックの状態を更新するメソッド
    def update(self, count):
        #下との衝突判定
        erased = 0
        #ブロックが重なる場合
        if is_overlapped(self.xpos, self.ypos + 1, self.turn):
            for y_offset in range(BLOCK.size):
                for x_offset in range(BLOCK.size):
                    if 0 <= self.xpos+x_offset < WIDTH and 0 <= self.ypos+y_offset < HEIGHT:
                        val = BLOCK.data[y_offset*BLOCK.size + x_offset]
                        #ブロックをコピー
                        if val != 0:
                            FIELD[self.ypos+y_offset][self.xpos+x_offset] = val

            #行の削除
            erased = erase_line()
            #次のブロックへ切り替え
            go_next_block(count)

        #ブロックの移動
        if self.fire < count:
            self.fire = count + INTERVAL
            self.ypos += 1
        return erased

    #ブロックを描画するメソッド
    def draw(self):
        for index in range(len(self.data)):
            xpos = index % self.size
            ypos = index // self.size
            val = self.data[index]
            if 0 <= ypos + self.ypos < HEIGHT and 0 <= xpos + self.xpos < WIDTH and val != 0:
                x_pos = 25 + (xpos + self.xpos) * 25
                y_pos = 25 + (ypos + self.ypos) * 25
                pygame.draw.rect(SURFACE, COLORS[val], (x_pos, y_pos, 24, 24))

#行が全て埋まった段を消す関数
def erase_line():
    erased = 0
    ypos = 20
    while ypos >= 0:
        #行が全て埋まった場合
        if all(FIELD[ypos]):
            #消去した行のカウンタ
            erased += 1
            del FIELD[ypos]
            #空の行を追加
            FIELD.insert(0, [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8])
        else:
            ypos -= 1
    return erased

#ゲームオーバーか否かを判定する関数
def is_game_over():
    filled = 0
    for cell in FIELD[0]:
        if cell != 0:
            filled += 1
    return filled > 2   #2 = 左右の壁

#次のブロックに切り替える関数
def go_next_block(count):
    global BLOCK, NEXT_BLOCK
    BLOCK = NEXT_BLOCK if NEXT_BLOCK != None else Block(count)
    NEXT_BLOCK = Block(count)

#ブロックが壁や他のブロックと衝突するか否かを判定する関数
def is_overlapped(xpos, ypos, turn):
    data = BLOCK.type[turn]
    for y_offset in range(BLOCK.size):
        for x_offset in range(BLOCK.size):
            if 0 <= xpos+x_offset < WIDTH and 0 <= ypos+y_offset < HEIGHT:
                if data[y_offset*BLOCK.size + x_offset] != 0 and FIELD[ypos+y_offset][xpos+x_offset] != 0:
                    return True
    return False

#グローバル変数
pygame.init()
pygame.key.set_repeat(150, 150)
SURFACE = pygame.display.set_mode([600, 600])
FPSCLOCK = pygame.time.Clock()
WIDTH = 12 #FIELDの幅
HEIGHT = 22 #FIELDの高さ
INTERVAL = 40 #何フレームでブロックが落下するかという間隔
FIELD = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)] #積み重なったブロックの状態を捧持する2次元配列
COLORS = ((0, 0, 0), (255, 165, 0), (0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0), (255, 0, 0), (128, 128, 128)) #色の配列
BLOCK = None #落下中のブロックオブジェクト
NEXT_BLOCK = None #次に落下するブロックオブジェクト

def main():
    global INTERVAL
    count = 0 #時間を管理するカウンタ
    score = 0 #得点
    game_over = False #ゲームオーバーか否かのフラグ
    smallfont = pygame.font.SysFont(None, 36)
    largefont = pygame.font.SysFont(None, 72)
    message_over = largefont.render("GAME OVER!!", True, (0, 255, 225))
    message_rect = message_over.get_rect()
    message_rect.center = (300, 300)

    #次に落下するブロックの初期化
    go_next_block(INTERVAL)

    #左右の壁と底を8、空白部分を0で埋める
    for ypos in range(HEIGHT):
        for xpos in range(WIDTH):
            FIELD[ypos][xpos] = 8 if xpos == 0 or xpos == WIDTH - 1 else 0
    for index in range(WIDTH):
        FIELD[HEIGHT-1][index] = 8

    while True:
        key = None
        for event in pygame.event.get():
            #ゲーム終了
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                key = event.key

        game_over = is_game_over()
        if not game_over:
            count += 5
            #INTERVSLの減少
            if count % 1000 == 0:
                INTERVAL = max(1, INTERVAL - 2)
            #消去した行数
            erased = BLOCK.update(count)

            #スコアの加算
            if erased > 0:
                score += (2 ** erased) * 100

            #キーイベント処理
            next_x, next_y, next_t = BLOCK.xpos, BLOCK.ypos, BLOCK.turn
            if key == K_SPACE:
                next_t = (next_t + 1) % 4
            elif key == K_RIGHT:
                next_x += 1
            elif key == K_LEFT:
                next_x -= 1
            elif key == K_DOWN:
                next_y += 1

            #ブロックがかさなっていない場合、キーの入力に応じてプロパティを更新
            if not is_overlapped(next_x, next_y, next_t):
                BLOCK.xpos = next_x
                BLOCK.ypos = next_y
                BLOCK.turn = next_t
                BLOCK.data = BLOCK.type[BLOCK.turn]

        #全体＆落下中のブロックの描画
        SURFACE.fill((0, 0, 0))
        for ypos in range(HEIGHT):
            for xpos in range(WIDTH):
                val = FIELD[ypos][xpos]
                pygame.draw.rect(SURFACE, COLORS[val], (xpos*25 + 25, ypos*25 + 25, 24, 24))
        BLOCK.draw()

        #次のブロックの描画
        for ypos in range(NEXT_BLOCK.size):
            for xpos in range(NEXT_BLOCK.size):
                val = NEXT_BLOCK.data[xpos + ypos*NEXT_BLOCK.size]
                pygame.draw.rect(SURFACE, COLORS[val], (xpos*25 + 460, ypos*25 + 100, 24, 24))

        #スコアの描画
        score_str = str(score).zfill(6)
        score_image = smallfont.render(score_str,  True, (0, 255, 0))
        SURFACE.blit(score_image, (500, 30))

        if game_over:
            SURFACE.blit(message_over, message_rect)

        pygame.display.update()
        FPSCLOCK.tick(15)

if __name__ == '__main__':
    main()
