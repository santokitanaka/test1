"""
インベーダーゲーム風シューティングゲーム
操作方法：
  ← →キー：自機を左右に動かす
  スペースキー：弾を撃つ
  Qキー：ゲームを終了する
"""

import pygame   # ゲームを作るためのライブラリ
import sys      # プログラムを終了するときに使う
import random   # 敵の動きにランダム性を入れるために使う

# ─── 色の設定（赤・緑・青の3つの数字で色を表す） ───────────────────
黒   = (0,   0,   0)
白   = (255, 255, 255)
赤   = (255,  50,  50)
緑   = (50,  255,  50)
青   = (100, 150, 255)
黄   = (255, 220,  50)
オレンジ = (255, 140,  0)

# ─── 画面サイズの設定 ─────────────────────────────────────────
画面の幅  = 640   # 横のドット数
画面の高さ = 540   # 縦のドット数

# ─── ゲームの速さ・大きさの設定 ──────────────────────────────────
フレームレート   = 60   # 1秒間に画面を何回書き直すか
自機の速さ       = 5    # 自機が1回に動くドット数
弾の速さ         = 8    # 弾が1回に動くドット数
敵弾の速さ       = 3    # 敵弾が1回に動くドット数
敵の横の速さ     = 1    # 敵が左右に動く速さ
敵の縦移動量     = 20   # 敵が端まで来たときに下に動く量


# ─── 自機クラス（プレイヤーが操作する宇宙船） ─────────────────────────
class 自機(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 自機の形を描く（三角形の宇宙船）
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, 緑, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.rect(self.image, 青, (15, 20, 10, 10))

        self.rect = self.image.get_rect()
        # 画面の中央下に配置する
        self.rect.centerx = 画面の幅 // 2
        self.rect.bottom   = 画面の高さ - 10

        self.弾クールダウン = 0   # 連射を防ぐためのタイマー

    def update(self):
        # キーボードの入力を調べる
        押されたキー = pygame.key.get_pressed()

        # ←キーが押されていたら左に移動
        if 押されたキー[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 自機の速さ

        # →キーが押されていたら右に移動
        if 押されたキー[pygame.K_RIGHT] and self.rect.right < 画面の幅:
            self.rect.x += 自機の速さ

        # クールダウンを1ずつ減らす
        if self.弾クールダウン > 0:
            self.弾クールダウン -= 1

    def 弾を撃てるか(self):
        # クールダウンが0になったら撃てる
        return self.弾クールダウン == 0

    def 弾を撃った(self):
        # 撃ったらクールダウンをリセットする（20フレーム待つ）
        self.弾クールダウン = 20


# ─── 自機の弾クラス ────────────────────────────────────────────
class 自機弾(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 弾の形（小さな黄色い四角）
        self.image = pygame.Surface((4, 14))
        self.image.fill(黄)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom   = y

    def update(self):
        # 弾は上に向かって進む
        self.rect.y -= 弾の速さ
        # 画面の外に出たら消す
        if self.rect.bottom < 0:
            self.kill()


# ─── 敵クラス ─────────────────────────────────────────────────
class 敵(pygame.sprite.Sprite):
    def __init__(self, x, y, 種類=0):
        super().__init__()
        # 種類によって敵の色を変える
        色一覧 = [赤, オレンジ, 白]
        色 = 色一覧[種類 % len(色一覧)]

        # 敵の形を描く（シンプルなエイリアン風）
        self.image = pygame.Surface((36, 28), pygame.SRCALPHA)
        # 胴体
        pygame.draw.rect(self.image, 色, (6, 8, 24, 14), border_radius=4)
        # 頭
        pygame.draw.ellipse(self.image, 色, (10, 0, 16, 14))
        # 目（黒い点）
        pygame.draw.circle(self.image, 黒, (14, 6), 3)
        pygame.draw.circle(self.image, 黒, (22, 6), 3)
        # 触角
        pygame.draw.line(self.image, 色, (12, 0), (8,  -4), 2)
        pygame.draw.line(self.image, 色, (24, 0), (28, -4), 2)
        # 足
        pygame.draw.line(self.image, 色, (10, 22), (6,  28), 2)
        pygame.draw.line(self.image, 色, (18, 22), (18, 28), 2)
        pygame.draw.line(self.image, 色, (26, 22), (30, 28), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.方向 = 1        # 1:右向き、-1:左向き
        self.種類  = 種類

    def update(self):
        # 左右に移動する（グループ全体で管理するので個別には動かさない）
        pass


# ─── 敵弾クラス ───────────────────────────────────────────────
class 敵弾(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 敵弾の形（赤い細長い四角）
        self.image = pygame.Surface((4, 12))
        self.image.fill(赤)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top      = y

    def update(self):
        # 敵弾は下に向かって進む
        self.rect.y += 敵弾の速さ
        # 画面の外に出たら消す
        if self.rect.top > 画面の高さ:
            self.kill()


# ─── 爆発エフェクトクラス ──────────────────────────────────────
class 爆発(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames  = []   # アニメーションのコマ一覧
        self.現在のコマ = 0
        self.タイマー = 0

        # 4段階の爆発を描く
        for 大きさ in [10, 20, 28, 16]:
            画像 = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(画像, オレンジ, (20, 20), 大きさ)
            pygame.draw.circle(画像, 黄,      (20, 20), max(大きさ - 6, 2))
            self.frames.append(画像)

        self.image = self.frames[0]
        self.rect  = self.image.get_rect(center=(x, y))

    def update(self):
        # 4フレームごとに次のコマに進む
        self.タイマー += 1
        if self.タイマー % 4 == 0:
            self.現在のコマ += 1
            if self.現在のコマ >= len(self.frames):
                self.kill()   # 全コマ終わったら消す
            else:
                self.image = self.frames[self.現在のコマ]


# ─── 敵を作る関数 ─────────────────────────────────────────────
def 敵を配置する():
    """敵のグループを作って返す"""
    グループ = pygame.sprite.Group()
    # 4行×10列の敵を並べる
    for 行 in range(4):
        for 列 in range(10):
            x = 60 + 列 * 54
            y = 60 + 行 * 50
            新しい敵 = 敵(x, y, 種類=行)
            グループ.add(新しい敵)
    return グループ


# ─── スコアを画面に表示する関数 ───────────────────────────────────
def テキスト表示(画面, テキスト, x, y, 色=白, 大きさ=22):
    フォント = pygame.font.Font(None, 大きさ)
    描画 = フォント.render(テキスト, True, 色)
    画面.blit(描画, (x, y))


# ─── メインの処理 ─────────────────────────────────────────────
def main():
    pygame.init()   # pygameを起動する
    画面 = pygame.display.set_mode((画面の幅, 画面の高さ))
    pygame.display.set_caption("インベーダーゲーム by Claude")
    時計 = pygame.time.Clock()

    # ゲームをリセットする関数（ゲームオーバー後の再スタート用）
    def ゲームを初期化する():
        my_自機   = 自機()
        自機グループ = pygame.sprite.GroupSingle(my_自機)
        自機弾グループ = pygame.sprite.Group()
        敵弾グループ   = pygame.sprite.Group()
        爆発グループ   = pygame.sprite.Group()
        my_敵グループ  = 敵を配置する()

        return {
            "自機": my_自機,
            "自機グループ": 自機グループ,
            "自機弾グループ": 自機弾グループ,
            "敵弾グループ": 敵弾グループ,
            "爆発グループ": 爆発グループ,
            "敵グループ": my_敵グループ,
            "スコア": 0,
            "残機": 3,
            "敵の移動方向": 1,      # 1:右、-1:左
            "敵の弾タイマー": 0,    # 敵が弾を撃つタイミング用
            "ゲームオーバー": False,
            "クリア": False,
        }

    ゲーム = ゲームを初期化する()
    実行中 = True

    # ─── ゲームのメインループ ────────────────────────────────────
    while 実行中:

        # ── イベント処理（キーが押されたか、ウィンドウを閉じたかを調べる） ──
        for イベント in pygame.event.get():
            if イベント.type == pygame.QUIT:
                実行中 = False   # ウィンドウの×ボタンで終了

            if イベント.type == pygame.KEYDOWN:
                # Qキーで終了
                if イベント.key == pygame.K_q:
                    実行中 = False

                # スペースキーで弾を撃つ
                if イベント.key == pygame.K_SPACE:
                    if (not ゲーム["ゲームオーバー"] and
                            not ゲーム["クリア"] and
                            ゲーム["自機"].弾を撃てるか()):
                        弾 = 自機弾(ゲーム["自機"].rect.centerx,
                                     ゲーム["自機"].rect.top)
                        ゲーム["自機弾グループ"].add(弾)
                        ゲーム["自機"].弾を撃った()

                # ゲームオーバーまたはクリア後、Rキーでリスタート
                if イベント.key == pygame.K_r:
                    if ゲーム["ゲームオーバー"] or ゲーム["クリア"]:
                        ゲーム = ゲームを初期化する()

        # ── ゲーム中の処理 ──────────────────────────────────────
        if not ゲーム["ゲームオーバー"] and not ゲーム["クリア"]:

            # 各グループを更新する
            ゲーム["自機グループ"].update()
            ゲーム["自機弾グループ"].update()
            ゲーム["敵弾グループ"].update()
            ゲーム["爆発グループ"].update()

            # ── 敵を左右に動かす ─────────────────────────────────
            敵リスト = ゲーム["敵グループ"].sprites()
            if 敵リスト:
                # 一番右と一番左にいる敵を調べる
                一番右 = max(e.rect.right  for e in 敵リスト)
                一番左 = min(e.rect.left   for e in 敵リスト)

                if 一番右 >= 画面の幅 - 5:
                    ゲーム["敵の移動方向"] = -1    # 右端に着いたら左に折り返す
                    for e in 敵リスト:
                        e.rect.y += 敵の縦移動量  # 下に下がる
                elif 一番左 <= 5:
                    ゲーム["敵の移動方向"] = 1     # 左端に着いたら右に折り返す
                    for e in 敵リスト:
                        e.rect.y += 敵の縦移動量  # 下に下がる

                # 全員を横に動かす
                for e in 敵リスト:
                    e.rect.x += 敵の横の速さ * ゲーム["敵の移動方向"]

                # ── 敵が弾をランダムに撃つ ───────────────────────
                ゲーム["敵の弾タイマー"] += 1
                # 約1秒（60フレーム）に1回、ランダムな敵が弾を撃つ
                if ゲーム["敵の弾タイマー"] >= random.randint(50, 90):
                    ゲーム["敵の弾タイマー"] = 0
                    射撃する敵 = random.choice(敵リスト)
                    敵の弾 = 敵弾(射撃する敵.rect.centerx,
                                   射撃する敵.rect.bottom)
                    ゲーム["敵弾グループ"].add(敵の弾)

                # ── 敵が自機の高さまで降りてきたらゲームオーバー ──
                if max(e.rect.bottom for e in 敵リスト) >= ゲーム["自機"].rect.top:
                    ゲーム["ゲームオーバー"] = True

            # ── 自機の弾が敵に当たったか調べる ───────────────────
            当たった結果 = pygame.sprite.groupcollide(
                ゲーム["敵グループ"], ゲーム["自機弾グループ"],
                True, True   # 当たったものを両方消す
            )
            for 倒された敵 in 当たった結果:
                # 爆発エフェクトを作る
                爆 = 爆発(倒された敵.rect.centerx, 倒された敵.rect.centery)
                ゲーム["爆発グループ"].add(爆)
                ゲーム["スコア"] += (倒された敵.種類 + 1) * 10   # 行によって得点が違う

            # ── 敵の弾が自機に当たったか調べる ───────────────────
            当たった敵弾 = pygame.sprite.spritecollide(
                ゲーム["自機"], ゲーム["敵弾グループ"], True
            )
            if 当たった敵弾:
                爆 = 爆発(ゲーム["自機"].rect.centerx,
                           ゲーム["自機"].rect.centery)
                ゲーム["爆発グループ"].add(爆)
                ゲーム["残機"] -= 1
                if ゲーム["残機"] <= 0:
                    ゲーム["ゲームオーバー"] = True
                else:
                    # 自機の位置を中央に戻す
                    ゲーム["自機"].rect.centerx = 画面の幅 // 2

            # ── 敵を全員倒したらクリア ────────────────────────────
            if len(ゲーム["敵グループ"]) == 0:
                ゲーム["クリア"] = True

        # ── 画面を描く ──────────────────────────────────────────
        画面.fill(黒)   # 背景を黒く塗りつぶす

        # 各グループを描く
        ゲーム["敵グループ"].draw(画面)
        ゲーム["自機グループ"].draw(画面)
        ゲーム["自機弾グループ"].draw(画面)
        ゲーム["敵弾グループ"].draw(画面)
        ゲーム["爆発グループ"].draw(画面)

        # スコアと残機を表示する
        テキスト表示(画面, f"SCORE: {ゲーム['スコア']}", 10, 10, 白, 28)
        テキスト表示(画面, f"LIFE: {'♥ ' * ゲーム['残機']}", 画面の幅 - 130, 10, 赤, 28)

        # ゲームオーバーの表示
        if ゲーム["ゲームオーバー"]:
            テキスト表示(画面, "GAME OVER",      200, 220, 赤,   52)
            テキスト表示(画面, f"SCORE: {ゲーム['スコア']}", 230, 290, 白,   32)
            テキスト表示(画面, "R キーで再スタート / Q キーで終了", 140, 340, 黄, 26)

        # クリアの表示
        if ゲーム["クリア"]:
            テキスト表示(画面, "STAGE CLEAR!",    175, 220, 緑,   52)
            テキスト表示(画面, f"SCORE: {ゲーム['スコア']}", 230, 290, 白,   32)
            テキスト表示(画面, "R キーで再スタート / Q キーで終了", 140, 340, 黄, 26)

        # 操作説明を画面下に表示する
        テキスト表示(画面, "←→:移動  スペース:弾  Q:終了", 160, 画面の高さ - 26, (100, 100, 100), 22)

        pygame.display.flip()       # 描いた内容を画面に反映する
        時計.tick(フレームレート)   # フレームレートを調整する

    pygame.quit()   # pygameを終了する
    sys.exit()      # プログラムを終了する


# ─── プログラムのスタート地点 ────────────────────────────────────
if __name__ == "__main__":
    main()  # ゲームを起動する
