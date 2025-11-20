"""
深さ制限付きCoach

alpha-zero-generalのCoachを拡張して、DepthLimitedMCTSを使用
"""

import os
import sys
import numpy as np
import logging
from collections import deque
from random import shuffle
from pickle import Pickler, Unpickler

# alpha-zero-generalをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'alpha-zero-general'))

from Coach import Coach
from DepthLimitedMCTS import DepthLimitedMCTS

log = logging.getLogger(__name__)


class DepthLimitedCoach(Coach):
    """
    深さ制限付きMCTSを使用するCoachクラス
    """
    
    def __init__(self, game, nnet, args):
        """
        Args:
            game: ゲームオブジェクト
            nnet: ニューラルネットワーク
            args: ハイパーパラメータ
        """
        # 親クラスの初期化の前に、argsを設定
        self.game = game
        self.nnet = nnet
        self.args = args
        self.pnet = self.nnet.__class__(self.game, self.args)  # previous net
        self.trainExamplesHistory = []
        self.skipFirstSelfPlay = False
        
        # MCTSを深さ制限付きMCTSで作成（親のMCTSを使わない）
        self.mcts = DepthLimitedMCTS(self.game, self.nnet, self.args)
        
        print(f"✅ 深さ制限付きMCTS作成完了")
        print(f"   最大深さ: {self.mcts.max_depth}")
    
    def executeEpisode(self):
        """
        1エピソードの自己対戦を実行
        
        Returns:
            trainExamples: 学習用データ [(board, pi, v), ...]
        """
        trainExamples = []
        board = self.game.getInitBoard()
        self.curPlayer = 1
        episodeStep = 0
        
        # MCTSが正しい型か確認
        if not isinstance(self.mcts, DepthLimitedMCTS):
            print(f"⚠️ MCTSが置き換えられています: {type(self.mcts)}")
            # 強制的にDepthLimitedMCTSに置き換え
            self.mcts = DepthLimitedMCTS(self.game, self.nnet, self.args)
            print(f"✅ DepthLimitedMCTSで再作成しました")
        
        # エピソード開始時に統計をリセット
        self.mcts.reset_stats()

        while True:
            episodeStep += 1
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)
            temp = int(episodeStep < self.args.tempThreshold)

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp)
            
            # デバッグ: piのサイズチェック（最初の手のみ）
            if episodeStep == 1:
                print(f"   デバッグ: pi shape = {len(pi)}, 期待値 = {self.game.getActionSize()}")
            
            sym = self.game.getSymmetries(canonicalBoard, pi)
            for b, p in sym:
                trainExamples.append([b, self.curPlayer, p, None])

            action = np.random.choice(len(pi), p=pi)
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)

            r = self.game.getGameEnded(board, self.curPlayer)

            if r != 0:
                # エピソード終了
                # 統計情報を表示
                stats = self.mcts.get_stats()
                print(f"   エピソード終了: {episodeStep}手")
                print(f"   最大探索深さ: {stats['max_depth_reached']}")
                print(f"   深さ制限到達回数: {stats['depth_limit_hits']}")
                print(f"   探索状態数: {stats['total_states']}")
                
                return [(x[0], x[2], r * ((-1) ** (x[1] != self.curPlayer))) for x in trainExamples]
            
            # 安全のため、最大手数制限
            if episodeStep > 200:
                print(f"   ⚠️ 最大手数到達（200手）、引き分けとして終了")
                return [(x[0], x[2], 0) for x in trainExamples]
    
    def learn(self):
        """
        学習プロセスを実行（評価結果の表示を追加）
        
        元のCoachのlearn()をコピーして、評価結果の表示を改善
        """
        from Arena import Arena
        from MCTS import MCTS
        from tqdm import tqdm
        
        for i in range(1, self.args.numIters + 1):
            # イテレーション開始
            log.info(f'Starting Iter #{i} ...')
            print(f"\n{'='*70}")
            print(f"イテレーション {i}/{self.args.numIters}")
            print(f"{'='*70}")
            
            # Self-play (自己対戦)
            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)
                
                for _ in tqdm(range(self.args.numEps), desc="Self Play"):
                    self.mcts = DepthLimitedMCTS(self.game, self.nnet, self.args)  # reset search tree
                    iterationTrainExamples += self.executeEpisode()
                
                # 学習データをヒストリーに追加
                self.trainExamplesHistory.append(iterationTrainExamples)
            
            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                log.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory)}")
                self.trainExamplesHistory.pop(0)
            
            # 学習例を保存
            self.saveTrainExamples(i)
            
            # 全ての学習データを使って訓練
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)
            
            # temp.pth.tarに保存（評価前の旧モデル）
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = DepthLimitedMCTS(self.game, self.pnet, self.args)
            
            # 新モデルを訓練
            self.nnet.train(trainExamples)
            nmcts = DepthLimitedMCTS(self.game, self.nnet, self.args)
            
            # 評価：新モデル vs 旧モデル
            log.info('PITTING AGAINST PREVIOUS VERSION')
            print(f"\n{'='*70}")
            print("評価対戦: 新モデル vs 旧モデル")
            print(f"{'='*70}")
            
            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare)
            
            # 結果表示（目立つように）
            print(f"\n{'='*70}")
            print(f"📊 評価結果")
            print(f"{'='*70}")
            print(f"  新モデルの勝利: {nwins}")
            print(f"  旧モデルの勝利: {pwins}")
            print(f"  引き分け: {draws}")
            if pwins + nwins > 0:
                win_rate = float(nwins) / (pwins + nwins)
                print(f"  新モデルの勝率: {win_rate:.1%}")
            print(f"{'='*70}\n")
            
            log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            
            # モデル更新の判定
            if pwins + nwins == 0 or float(nwins) / (pwins + nwins) < self.args.updateThreshold:
                log.info('REJECTING NEW MODEL')
                print(f"❌ 新モデルを不採用（勝率が閾値 {self.args.updateThreshold:.0%} 未満）\n")
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                log.info('ACCEPTING NEW MODEL')
                print(f"✅ 新モデルを採用！best.pth.tarを更新\n")
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')
    
    def getCheckpointFile(self, iteration):
        """チェックポイントファイル名を生成"""
        return 'checkpoint_' + str(iteration) + '.pth.tar'
    
    def saveTrainExamples(self, iteration):
        """学習データを保存"""
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

