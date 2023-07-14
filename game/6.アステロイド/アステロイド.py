import sys
from math import radians, sin, cos
from random import randint
import pygame
from pygame.locals import Rect, QUIT, KEYDOWN, KEYUP, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN

pygame.init()
pygame.key.set_repeat(5, 5)
SURFACE = pygame.display.set_mode((800, 600))
FPSCLOCK = pygame.time.Clock()

#全ての描画オブジェクトの親クラス 
class Drawable:
    def __init__(self, rect):
        self.rect = rect #描画する短形
        self.step = [0, 0] #1コマで移動する量

    #描画対象を移動するメソッド
    def move(self):
        rect = self.rect.center
        #画面の端に到達したら逆側に現れる
        xpos = (rect[0] + self.step[0]) % 800
        ypos = (rect[1] + self.step[1]) % 600
        self.rect.center = (xpos, ypos)

#隕石オブジェクト
class Rock(Drawable):
    def __init__(self, pos, size):
        #親クラスの初期化
        super(Rock, self).__init__(Rect(0, 0, size, size))
        self.rect.center = pos
        self.image = pygame.image.load("rock.png") #隕石の画像イメージ
        self.theta = randint(0, 360) #隕石が移動する方向
        self.size = size #隕石のサイズ
        self.power = 128 / size #移動スピード
        self.step[0] = cos(radians(self.theta)) * self.power
        self.step[1] = sin(radians(self.theta)) * -self.power

    #隕石を描画するメソッド
    def draw(self):
        rotated = pygame.transform.rotozoom(self.image, self.theta, self.size / 64)
        rect = rotated.get_rect()
        rect.center = self.rect.center
        SURFACE.blit(rotated, rect)

    #隕石を移動するメソッド
    def tick(self):
        self.theta += 3
        self.move()

#弾丸オブジェクト
class Shot(Drawable):
    def __init__(self):
        #親クラスの初期化
        super(Shot, self).__init__(Rect(0, 0, 6, 6))
        self.count = 40 #弾丸がどれだけ進んだかを示すカウンタ
        self.power = 10 #弾丸の速度
        self.max_count = 40 #弾丸の最大到達距離

    #弾丸を描画するメソッド
    def draw(self):
        if self.count < self.max_count:
            pygame.draw.rect(SURFACE, (225, 225, 0), self.rect)

    #弾丸を移動するメソッド
    def tick(self):
        self.count += 1
        self.move()

#自機オブジェクト
class Ship(Drawable):
    def __init__(self):
        #親クラスの初期化
        super(Ship, self).__init__(Rect(355, 270, 90, 60))
        self.theta = 0 #自機の向き
        self.power = 0 #自機の速度
        self.accel = 0 #自機の加速度
        self.explode = False #自機が爆発したか否かのフラグ
        self.image = pygame.image.load("ship.png") #自機の画像
        self.bang = pygame.image.load("bang.png") #爆発時の画像

    #自機を描画するメソッド
    def draw(self):
        rotated = pygame.transform.rotate(self.image, self.theta)
        rect = rotated.get_rect()
        rect.center = self.rect.center
        SURFACE.blit(rotated, rect)
        if self.explode:
            SURFACE.blit(self.bang, rect)

    #自機を動かすメソッド
    def tick(self):
        self.power += self.accel
        self.power *= 0.94
        self.accel *= 0.94
        self.step[0] = cos(radians(self.theta)) * self.power
        self.step[1] = sin(radians(self.theta)) * -self.power
        self.move()

#キーイベントを処理する関数
def key_event_handler(keymap, ship):
    for event in pygame.event.get():
        #ゲーム終了
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        #イベントをkeymapに追加
        elif event.type == KEYDOWN:
            if not event.key in keymap:
                keymap.append(event.key)
        #イベントをkeymapから削除
        elif event.type == KEYUP:
            keymap.remove(event.key)

    #キーの入力に応じて自機の移動を制御
    if K_LEFT in keymap:
        ship.theta += 5
    elif K_RIGHT in keymap:
        ship.theta -= 5
    elif K_UP in keymap:
        ship.accel = min(5, ship.accel + 0.2)
    elif K_DOWN in keymap:
        ship.accel = max(-5, ship.accel - 0.1)

def main():
    sysfont = pygame.font.SysFont(None, 72)
    scorefont = pygame.font.SysFont(None, 36)
    message_clear = sysfont.render("!!CLEARED!!", True, (0, 255, 225))
    message_over = sysfont.render("GAME OVER!!", True, (0, 255, 225))
    message_rect = message_clear.get_rect()
    message_rect.center = (400, 300)

    keymap = [] #押されているキーのコードを保持するリスト
    shots = [] #弾丸オブジェクトを格納するリスト
    rocks = [] #隕石オブジェクトを格納するリスト
    ship = Ship() #自機
    game_over = False #ゲームオーバーか否かのフラグ
    score = 0 #得点
    back_x, back_y = 0, 0 #背景画像をずらす量
    back_image = pygame.image.load("bg.png") #背景画像
    back_image = pygame.transform.scale2x(back_image)

    #7個の弾丸を格納
    while len(shots) < 7:
        shots.append(Shot())

    #4個の隕石を自機と重ならないように配置
    while len(rocks) < 4:
        pos = randint(0, 800), randint(0, 600)
        rock = Rock(pos, 64)
        if not rock.rect.colliderect(ship.rect):
            rocks.append(rock)

    while True:
        #キーの処理
        key_event_handler(keymap, ship)

        if not game_over:
            #自機の移動
            ship.tick()

            # 隕石の移動
            for rock in rocks:
                rock.tick()
                #衝突判定
                if rock.rect.colliderect(ship.rect):
                    ship.explode = True
                    game_over = True

            # 弾丸の移動
            fire = False
            for shot in shots:
                if shot.count < shot.max_count:
                    shot.tick()

                    # 弾丸と隕石の衝突処理
                    hit = None
                    for rock in rocks:
                        if rock.rect.colliderect(shot.rect):
                            hit = rock
                    if hit != None:
                        score += hit.rect.width * 10
                        shot.count = shot.max_count
                        rocks.remove(hit)
                        if hit.rect.width > 36:
                            rocks.append(Rock(hit.rect.center, hit.rect.width * 0.75))
                            rocks.append(Rock(hit.rect.center, hit.rect.width * 0.75))
                        if len(rocks) == 0:
                            game_over = True

                #弾丸の発射
                elif not fire and K_SPACE in keymap:
                    shot.count = 0
                    shot.rect.center = ship.rect.center
                    shot_x = shot.power * cos(radians(ship.theta))
                    shot_y = shot.power * -sin(radians(ship.theta))
                    shot.step = (shot_x, shot_y)
                    fire = True

        #背景の描画
        back_x = (back_x + ship.step[0] / 2) % 1600
        back_y = (back_y + ship.step[1] / 2) % 1600
        SURFACE.fill((0, 0, 0))
        SURFACE.blit(back_image, (-back_x, -back_y), (0, 0, 3200, 3200))

        #各種オブジェクトの描画
        ship.draw()
        for shot in shots:
            shot.draw()
        for rock in rocks:
            rock.draw()

        #スコアの描画
        score_str = str(score).zfill(6)
        score_image = scorefont.render(score_str, True, (0, 255, 0))
        SURFACE.blit(score_image, (700, 10))

        #メッセージの描画
        if game_over:
            if len(rocks) == 0:
                SURFACE.blit(message_clear, message_rect.topleft)
            else:
                SURFACE.blit(message_over, message_rect.topleft)

        pygame.display.update()
        FPSCLOCK.tick(20)

if __name__ == '__main__':
    main()
