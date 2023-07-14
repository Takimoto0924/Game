import sys
import math
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, Rect

#ブロック・ボール・パドルオブジェクト
class Block:
    def __init__(self, col, rect, speed=0):
        self.col = col #塗りつぶし色
        self.rect = rect #描画する短形
        self.speed = speed #ボールの移動速度
        self.dir = random.randint(-45, 45) + 270 #ボールの移動の向き

    #ボールを動かすメソッド
    def move(self):
        self.rect.centerx += math.cos(math.radians(self.dir)) * self.speed
        self.rect.centery -= math.sin(math.radians(self.dir)) * self.speed

    #ブロック・ボール・パドルを描画するメソッド
    def draw(self):
        #スピードが0の場合は短形
        if self.speed == 0:
            pygame.draw.rect(SURFACE, self.col, self.rect)
        #スピードが0でない場合は円
        else:
            pygame.draw.ellipse(SURFACE, self.col, self.rect)

#毎フレーム呼び出されるメソッド
def tick():
    global BLOCKS
    for event in pygame.event.get():
        #ゲーム終了
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        #キーの入力に応じてパドルを移動
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                PADDLE.rect.centerx -= 10
            elif event.key == K_RIGHT:
                PADDLE.rect.centerx += 10
    #ボールを移動
    if BALL.rect.centery < 1000:
        BALL.move()

    """ブロックとの衝突判定"""
    #衝突前のブロック数
    prevlen = len(BLOCKS)
    #ボールと衝突したブロックを削除
    BLOCKS = [x for x in BLOCKS if not x.rect.colliderect(BALL.rect)]
    #衝突した場合、ボールの向きを変更
    if len(BLOCKS) != prevlen:
        BALL.dir *= -1

    """パドルとの衝突判定"""
    #パドルとの衝突場所によって反射角を調整
    if PADDLE.rect.colliderect(BALL.rect):
        BALL.dir = 90 + (PADDLE.rect.centerx - BALL.rect.centerx) / PADDLE.rect.width * 80

    """壁と衝突判定"""
    #壁と衝突した場合、ボールの向きを変更
    if BALL.rect.centerx < 0 or BALL.rect.centerx > 800:
        BALL.dir = 180 - BALL.dir
    if BALL.rect.centery < 0:
        BALL.dir = -BALL.dir
        BALL.speed = 15

pygame.init()
pygame.key.set_repeat(5, 5)
SURFACE = pygame.display.set_mode((800, 600))
FPSCLOCK = pygame.time.Clock()

BLOCKS = [] #ブロックオブジェクトを格納するリスト
PADDLE = Block((242, 242, 0), Rect(350, 550, 100, 20)) #パドルオブジェクト
BALL = Block((242, 242, 0), Rect(400, 300, 20, 20), 10) #ボールオブジェクト

def main():
    myfont = pygame.font.SysFont(None, 80)
    mess_clear = myfont.render("Cleared!", True, (255, 255, 0))
    mess_over = myfont.render("Game Over!", True, (255, 255, 0))
    colors = [(255, 0, 0), (255, 165, 0), (242, 242, 0), (0, 128, 0), (128, 0, 128), (0, 0, 250)]

    #ブロックの場所と色を決定
    for ypos, color in enumerate(colors, start=0):
        for xpos in range(0, 7):
            BLOCKS.append(Block(color, Rect(xpos * 100 + 60, ypos * 40 + 40, 80, 20)))

    while True:
        #フレームごとの処理
        tick()

        #描画
        SURFACE.fill((0, 0, 0))
        BALL.draw()
        PADDLE.draw()
        for block in BLOCKS:
            block.draw()

        #クリアのメッセージを描画
        if len(BLOCKS) == 0:
            SURFACE.blit(mess_clear, (300, 300))
        #ゲームオーバーのメッセージを描画
        if BALL.rect.centery > 800 and len(BLOCKS) > 0:
            SURFACE.blit(mess_over, (250, 300))

        pygame.display.update()
        FPSCLOCK.tick(30)

if __name__ == '__main__':
    main()
