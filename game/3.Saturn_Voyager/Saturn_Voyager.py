import sys
from random import randint
import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN

pygame.init()
SURFACE = pygame.display.set_mode((800, 600))
FPSCLOCK = pygame.time.Clock()

def main():
    game_over = False #ゲームオーバーか否かのフラグ
    score = 0 #スコア
    speed = 25 #スピード
    stars = [] #隕石を格納するリスト
    keymap = [] #どのキーが押下されているかを示すリスト
    ship = [0, 0] #自機の座標
    scope_image = pygame.image.load("scope.png") #照準器の画像
    rock_image = pygame.image.load("rock.png") #隕石の画像

    #メッセージ表示に関わるローカル変数
    scorefont = pygame.font.SysFont(None, 36)
    sysfont = pygame.font.SysFont(None, 72)
    message_over = sysfont.render("GAME OVER!!", True, (0, 255, 225))
    message_rect = message_over.get_rect()
    message_rect.center = (400, 400)

    #200個の隕石をランダムに配置
    while len(stars) < 200:
        stars.append({
            "pos": [randint(-1600, 1600), randint(-1200, 1200), randint(0, 4095)], #隕石の座標
            "theta": randint(0, 360) #回転角
        })

    while True:
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

        # フレーム毎の処理
        if not game_over:
            score += 1
            if score % 10 == 0:
                speed += 1

            if K_LEFT in keymap:
                ship[0] -= 30
            elif K_RIGHT in keymap:
                ship[0] += 30
            elif K_UP in keymap:
                ship[1] -= 30
            elif K_DOWN in keymap:
                ship[1] += 30

            #自機の座標を更新
            ship[0] = max(-800, min(800, ship[0]))
            ship[1] = max(-800, min(800, ship[1]))

            #隕石の座標を更新
            for star in stars:
                star["pos"][2] -= speed
                #衝突判定
                if star["pos"][2] < 64:
                    #隕石と自機のx軸方向、y軸方向の距離がともに50未満のとき衝突
                    if abs(star["pos"][0] - ship[0]) < 50 and abs(star["pos"][1] - ship[1]) < 50:
                        game_over = True
                    #衝突していない時、隕石を一番遠い位置に配置
                    star["pos"] = [randint(-1600, 1600), randint(-1600, 1600), 4095]

        # 描画
        SURFACE.fill((0, 0, 0))
        #遠くにある隕石を先に描画
        stars = sorted(stars, key=lambda x: x["pos"][2],  reverse=True)
        for star in stars:
            zpos = star["pos"][2]
            xpos = ((star["pos"][0] - ship[0]) << 9) / zpos + 400
            ypos = ((star["pos"][1] - ship[1]) << 9) / zpos + 300
            size = (50 << 9) / zpos
            rotated = pygame.transform.rotozoom(rock_image, star["theta"], size / 145)
            SURFACE.blit(rotated, (xpos, ypos))

        #照準器の描画
        SURFACE.blit(scope_image, (0, 0))

        #ゲームオーバーのメッセージの描画
        if game_over:
            SURFACE.blit(message_over, message_rect)
            pygame.mixer.music.stop()

        # スコアの描画
        score_str = str(score).zfill(6)
        score_image = scorefont.render(score_str, True, (0, 255, 0))
        SURFACE.blit(score_image, (700, 50))

        pygame.display.update()
        FPSCLOCK.tick(20)

if __name__ == '__main__':
    main()
