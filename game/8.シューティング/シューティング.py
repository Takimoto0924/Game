import sys
from random import randint
import pygame
from pygame.locals import Rect, QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_SPACE

pygame.init()
pygame.key.set_repeat(5, 5)
SURFACE = pygame.display.set_mode((800, 600))
FPSCLOCK = pygame.time.Clock()

#全ての描画オブジェクトの親クラス
class Drawable:
    def __init__(self, rect, offset0, offset1):
        strip = pygame.image.load("strip.png")
        self.images = (pygame.Surface((24, 24), pygame.SRCALPHA), pygame.Surface((24, 24), pygame.SRCALPHA)) #描画する画像の配列
        self.rect = rect #描画する位置と大きさ
        self.count = 0 #描画する画像を切り替えるためのカウンタ
        self.images[0].blit(strip, (0, 0), Rect(offset0, 0, 24, 24))
        self.images[1].blit(strip, (0, 0), Rect(offset1, 0, 24, 24))

    #オブジェクトを移動するメソッド
    def move(self, diff_x, diff_y):
        self.count += 1
        self.rect.move_ip(diff_x, diff_y)

    #オブジェクトを描画するメソッド
    def draw(self):
        image = self.images[0] if self.count % 2 == 0 else self.images[1]
        SURFACE.blit(image, self.rect.topleft)

#自機オブジェクト
class Ship(Drawable):
    def __init__(self):
        super().__init__(Rect(400, 550, 24, 24), 192, 192)

#ビームオブジェクト
class Beam(Drawable):
    def __init__(self):
        super().__init__(Rect(400, 0, 24, 24), 0, 24)

#爆弾オブジェクト
class Bomb(Drawable):
    def __init__(self):
        super().__init__(Rect(400, -50, 24, 24), 48, 72)
        #爆弾の投下タイミング
        self.time = randint(5, 220)

#エイリアンオブジェクト
class Alien(Drawable):
    def __init__(self, rect, offset, score):
        super().__init__(rect, offset, offset+24)
        self.score = score

def main():
    sysfont = pygame.font.SysFont(None, 72)
    scorefont = pygame.font.SysFont(None, 36)
    message_clear = sysfont.render("!!CLEARED!!", True, (0, 255, 225))
    message_over = sysfont.render("GAME OVER!!", True, (0, 255, 225))
    message_rect = message_clear.get_rect()
    message_rect.center = (400, 300)
    game_over = False #ゲームオーバーか否か
    moving_left = True #エイリアン全体が左方向へ動いているか否か
    moving_down = False #エイリアン全体が下方向へ動いているか否か
    move_interval = 20 #エイリアンが移動するまでのフレーム数
    counter = 0 #時刻管理用のカウンタ
    score = 0 #点数
    aliens = [] #エイリアンオブジェクトを格納するリスト
    bombs = [] #爆弾オブジェクトを格納するリスト
    ship = Ship() #自機オブジェクト
    beam = Beam() #ビームオブジェクト

    #エイリアンの並びを初期化
    for ypos in range(4):
        offset = 96 if ypos < 2 else 144
        for xpos in range(13):
            rect = Rect(100+xpos*50, ypos*50 + 50, 24, 24)
            alien = Alien(rect, offset, (4-ypos)*10)
            aliens.append(alien)

    #爆弾を設定
    for _ in range(4):
        bombs.append(Bomb())

    while True:
        #自機の移動距離
        ship_move_x = 0
        for event in pygame.event.get():
            #ゲーム終了
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                #自機の移動量
                if event.key == K_LEFT:
                    ship_move_x = -5
                elif event.key == K_RIGHT:
                    ship_move_x = +5
                #ビーム位置の初期化
                elif event.key == K_SPACE and beam.rect.bottom < 0:
                    beam.rect.center = ship.rect.center

        if not game_over:
            counter += 1
            # 自機を移動
            ship.move(ship_move_x, 0)

            # ビームを移動
            beam.move(0, -15)

            """エイリアンを移動"""
            area = aliens[0].rect.copy()
            #全てのエイリアンを含むように短形のサイズを変更
            for alien in aliens:
                area.union_ip(alien.rect)

            if counter % move_interval == 0:
                move_x = -5 if moving_left else 5
                move_y = 0

                if (area.left < 10 or area.right > 790) and not moving_down:
                    #左右の移動方向の反転
                    moving_left = not moving_left
                    #下方向へ移動
                    move_x, move_y = 0, 24
                    #移動速度の上昇
                    move_interval = max(1, move_interval - 2)
                    moving_down = True
                else:
                    moving_down = False

                for alien in aliens:
                    alien.move(move_x, move_y)

            if area.bottom > 550:
                game_over = True

            for bomb in bombs:
                #爆弾を投下
                if bomb.time < counter and bomb.rect.top < 0:
                    #爆弾を投下するエイリアン
                    enemy = aliens[randint(0, len(aliens) - 1)]
                    bomb.rect.center = enemy.rect.center

                #爆弾が投下中
                if bomb.rect.top > 0:
                    bomb.move(0, 10)

                #爆弾が下まで到達
                if bomb.rect.top > 600:
                    bomb.time += randint(50, 250)
                    #待機状態
                    bomb.rect.top = -50

                #爆弾と自機の衝突判定
                if bomb.rect.colliderect(ship.rect):
                    game_over = True

            #ビームとエイリアンの衝突判定
            tmp = []
            for alien in aliens:
                if alien.rect.collidepoint(beam.rect.center):
                    #待機状態
                    beam.rect.top = -50
                    #スコアを加算
                    score += alien.score
                else:
                    tmp.append(alien)
            #ビームが衝突したエイリアンを削除
            aliens = tmp
            if len(aliens) == 0:
                game_over = True

        #描画
        SURFACE.fill((0, 0, 0))
        for alien in aliens:
            alien.draw()
        ship.draw()
        beam.draw()
        for bomb in bombs:
            bomb.draw()

        score_str = str(score).zfill(5)
        score_image = scorefont.render(score_str, True, (0, 255, 0))
        SURFACE.blit(score_image, (700, 10))

        if game_over:
            if len(aliens) == 0:
                SURFACE.blit(message_clear, message_rect.topleft)
            else:
                SURFACE.blit(message_over, message_rect.topleft)

        pygame.display.update()
        FPSCLOCK.tick(20)

if __name__ == '__main__':
    main()
