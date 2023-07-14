import sys
from random import randint
from math import hypot
import pygame
from pygame.locals import Rect, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN

#家のオブジェクト
class House:
    def __init__(self, xpos):
        self.rect = Rect(xpos, 550, 40, 40) #家の位置とサイズ
        self.exploded = False #爆発したか否か
        strip = pygame.image.load("strip.png")
        self.images = (pygame.Surface((20, 20), pygame.SRCALPHA), pygame.Surface((20, 20), pygame.SRCALPHA)) #通常画像と爆発時の画像
        self.images[0].blit(strip, (0, 0), Rect(0, 0, 20, 20))
        self.images[1].blit(strip, (0, 0), Rect(20, 0, 20, 20))

    #家を描画するメソッド
    def draw(self):
        if self.exploded:
            SURFACE.blit(self.images[1], self.rect.topleft)
        else:
            SURFACE.blit(self.images[0], self.rect.topleft)

#落下するミサイルオブジェクト
class Missile:
    def __init__(self):
        self.max_count = 500 #発射から地面到着までに要する時間
        self.interval = 1000 #落下と落下の間隔
        self.pos = [0, 0] #落下座標
        self.cpos = [0, 0] #現在落下中の座標
        self.firetime = 0 #落下開始時刻
        self.radius = 0 #爆風の半径
        self.reload(0)

    #ミサイルを初期化するメソッド
    def reload(self, time_count):
        house_x = randint(0, 12) * 60 + 20
        self.pos = (randint(0, 800), house_x)
        self.interval = int(self.interval * 0.9)
        self.firetime = randint(0, self.interval) + time_count
        self.cpos = [0, 0]
        self.radius = 0

    #ミサイルの状態を更新するメソッド
    def tick(self, time_count, shoot, houses):
        is_hit = False
        elapsed = time_count - self.firetime
        if elapsed < 0:
            return

        #爆発中
        if self.radius > 0:
            self.radius += 1
            #爆発終了
            if self.radius > 100:
                self.reload(time_count)
        #ミサイルが移動中
        else:
            self.cpos[0] = (self.pos[1]-self.pos[0]) * elapsed / self.max_count + self.pos[0]
            self.cpos[1] = 575 * elapsed / self.max_count

            #撃ち落とされたかどうかの判定
            diff = hypot(shoot.shot_pos[0] - self.cpos[0], shoot.shot_pos[1] - self.cpos[1])
            #迎撃
            if diff < shoot.radius:
                is_hit = True
                # 爆発開始
                self.radius = 1

            #地面との衝突判定
            if elapsed > self.max_count:
                #爆発開始
                self.radius = 1
                for house in houses:
                    #家の破壊
                    if hypot(self.cpos[0]-house.rect.center[0], self.cpos[1]-house.rect.center[1]) < 30:
                        house.exploded = True
        return is_hit

    #ミサイルを描画するメソッド
    def draw(self):
        pygame.draw.line(SURFACE, (0, 255, 255), (self.pos[0], 0), self.cpos)

        # 爆発中
        if self.radius > 0:
            rad = self.radius if self.radius < 50 else 100 - self.radius
            pos = (int(self.cpos[0]), int(self.cpos[1]))
            pygame.draw.circle(SURFACE, (0, 255, 255), pos, rad)

#自分の発射するビームオブジェクト
class Shoot:
    def __init__(self):
        self.scope = (400, 300) #照準器の中心座標
        self.image = pygame.image.load("scope.png") #照準器の画像
        self.count = 0 #発射してからのカウント
        self.fire = False #発射中か否かのフラグ
        self.radius = 0 #爆発の半径
        self.shot_pos = (0, 0) #現在の弾頭の位置

    #発射中のビームの位置・状態を更新するメソッド
    def tick(self):
        if self.fire:
            self.count += 1

            if 25 <= self.count < 50:
                self.radius += 2
            elif self.count >= 50:
                self.radius = 0
                self.fire = False
                self.count = 0

    #ビームを描画するメソッド
    def draw(self):
        rect = self.image.get_rect()
        rect.center = self.scope
        SURFACE.blit(self.image, rect)
        if not self.fire:
            return

        #爆発前
        if self.radius == 0 and self.count < 25:
            ratio = self.count / 25
            ypos = 600 - (600 - self.shot_pos[1]) * ratio
            x_left = int((self.shot_pos[0]) * ratio)
            x_right = int((800 - (800 - self.shot_pos[0]) * ratio))
            pygame.draw.line(SURFACE, (0, 255, 0), (0, 600), (x_left, ypos))
            pygame.draw.line(SURFACE, (0, 255, 0), (800, 600), (x_right, ypos))
        #爆発中
        elif self.radius > 0:
            pygame.draw.circle(SURFACE, (0, 255, 0), self.shot_pos, self.radius)

# グローバル変数
pygame.init()
SURFACE = pygame.display.set_mode([800, 600])
FPSCLOCK = pygame.time.Clock()

def main():
    game_over = False #ゲームオーバーか否かのフラグ
    missiles = [] #ミサイルオブジェクトを格納するリスト
    score = 0 #得点
    time_count = 0 #経過時間を管理するタイマー
    shoot = Shoot() #自分が発射した迎撃ミサイルオブジェクト
    houses = [] #家オブジェクトを格納したリスト

    scorefont = pygame.font.SysFont(None, 36)
    sysfont = pygame.font.SysFont(None, 72)
    message_over = sysfont.render("GAME OVER!!", True, (0, 255, 225))
    message_rect = message_over.get_rect()
    message_rect.center = (400, 300)

    #家を格納
    for index in range(13):
        houses.append(House(index*60 + 20))
    #ミサイルを格納
    while len(missiles) < 18:
        missiles.append(Missile())

    while True:
        #時間の経過
        time_count += 1
        for event in pygame.event.get():
            #ゲーム終了
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #照準器の座標
            elif event.type == MOUSEMOTION:
                shoot.scope = event.pos
            #迎撃ミサイルの発射
            elif event.type == MOUSEBUTTONDOWN:
                if not shoot.fire:
                    shoot.shot_pos = shoot.scope
                    shoot.fire = True

        """フレーム毎の処理"""
        #爆発した家の数
        exploded = len([x for x in houses if x.exploded])
        #全ての家が爆発したらゲームオーバー
        game_over = (exploded == 13)
        if not game_over:
            for missile in missiles:
                is_hit = missile.tick(time_count, shoot, houses)
                #迎撃できた場合、スコアを加算
                if is_hit:
                    score += 100
            shoot.tick()

        # 描画
        SURFACE.fill((0, 0, 0))
        shoot.draw()
        for house in houses:
            house.draw()
        for missile in missiles:
            missile.draw()

        score_str = str(score).zfill(6)
        score_image = scorefont.render(score_str, True, (0, 255, 0))
        SURFACE.blit(score_image, (700, 10))

        if game_over:
            SURFACE.blit(message_over, message_rect)

        pygame.display.update()
        FPSCLOCK.tick(20)

if __name__ == '__main__':
    main()
