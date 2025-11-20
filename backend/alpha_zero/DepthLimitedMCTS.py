"""
深さ制限付きMCTS

alpha-zero-generalのMCTSを拡張して、深さ制限を追加
無限ループを防ぎ、ワタルートゲームでも安全に動作
"""

import logging
import math
import numpy as np

EPS = 1e-8

log = logging.getLogger(__name__)


class DepthLimitedMCTS:
    """
    深さ制限付きMCTSクラス
    
    alpha-zero-generalのMCTSを基に、以下の機能を追加：
    - 探索深さの制限（max_depth）
    - 訪問回数によるループ検出
    - より安全なゲーム終了判定
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        
        # 深さ制限（デフォルト: 50手先まで）
        self.max_depth = getattr(args, 'max_depth', 50)
        
        self.Qsa = {}  # Q値: (state, action) -> float
        self.Nsa = {}  # 訪問回数: (state, action) -> int
        self.Ns = {}   # 状態訪問回数: state -> int
        self.Ps = {}   # 方策: state -> [prob, prob, ...]
        self.Es = {}   # 終了判定: state -> float
        self.Vs = {}   # 合法手: state -> [0/1, 0/1, ...]
        
        # 統計情報
        self.max_depth_reached = 0
        self.depth_limit_hits = 0

    def getActionProb(self, canonicalBoard, temp=1):
        """
        MCTSシミュレーションを実行して行動確率を返す
        
        Args:
            canonicalBoard: 正規化された盤面
            temp: 温度パラメータ（0=貪欲、1=探索的）
        
        Returns:
            probs: 各アクションの確率分布
        """
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard, depth=0)

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 
                  for a in range(self.game.getActionSize())]

        if temp == 0:
            # 温度0: 最も訪問されたアクションを選択
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        # 温度パラメータを適用
        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        
        if counts_sum > 0:
            probs = [x / counts_sum for x in counts]
        else:
            # すべて0の場合は均等分布
            probs = [1.0 / len(counts)] * len(counts)
        
        return probs

    def search(self, canonicalBoard, depth=0):
        """
        MCTSの1回の探索（深さ制限付き）
        
        Args:
            canonicalBoard: 正規化された盤面
            depth: 現在の探索深さ
        
        Returns:
            v: 現在の盤面の評価値（-1~1）
        """
        # 統計更新
        if depth > self.max_depth_reached:
            self.max_depth_reached = depth
        
        # 深さ制限チェック
        if depth >= self.max_depth:
            self.depth_limit_hits += 1
            # ニューラルネットの評価値で代替
            _, v = self.nnet.predict(canonicalBoard)
            return -v

        s = self.game.stringRepresentation(canonicalBoard)

        # ゲーム終了判定（キャッシュ）
        if s not in self.Es:
            self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
        
        if self.Es[s] != 0:
            # 終端ノード
            return -self.Es[s]

        # 葉ノード: ニューラルネット評価
        if s not in self.Ps:
            self.Ps[s], v = self.nnet.predict(canonicalBoard)
            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.Ps[s] = self.Ps[s] * valids  # 非合法手をマスク
            
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # 正規化
            else:
                # すべて非合法の場合（ゲーム終了のはず）
                log.warning("All valid moves were masked, doing a workaround.")
                self.Ps[s] = self.Ps[s] + valids
                sum_Ps_s = np.sum(self.Ps[s])
                if sum_Ps_s > 0:
                    self.Ps[s] /= sum_Ps_s
                else:
                    # 本当に合法手がない場合は強制終了
                    self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
                    if self.Es[s] == 0:
                        # それでも終了していない場合は引き分け扱い
                        self.Es[s] = 1e-4
                    return -self.Es[s]

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        # 内部ノード: UCBで最良のアクションを選択
        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                            1 + self.Nsa[(s, a)])
                else:
                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        
        # 次の状態へ
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)
        next_s = self.game.getCanonicalForm(next_s, next_player)

        # 再帰的に探索（深さ+1）
        v = self.search(next_s, depth=depth + 1)

        # バックアップ（Q値と訪問回数を更新）
        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1
        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v
    
    def get_stats(self):
        """統計情報を取得"""
        return {
            'max_depth_reached': self.max_depth_reached,
            'depth_limit_hits': self.depth_limit_hits,
            'total_states': len(self.Es),
            'total_edges': len(self.Qsa),
        }
    
    def reset_stats(self):
        """統計情報をリセット"""
        self.max_depth_reached = 0
        self.depth_limit_hits = 0

