"""
モンテカルロ木探索（MCTS）実装

ワタルートゲーム用のMCTSアルゴリズム。
UCB1を使った選択と、ランダムプレイアウトによるシミュレーションを実装。
"""

import math
import random
import time
from typing import Optional, List, Dict
from dataclasses import dataclass

import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from game.game import WataruToGame
from game.move import Move


@dataclass
class MCTSStats:
    """MCTS統計情報"""
    nodes_explored: int = 0
    simulations_run: int = 0
    time_elapsed: float = 0.0
    best_move_visits: int = 0
    best_move_win_rate: float = 0.0


class MCTSNode:
    """MCTSのノード（ゲーム状態）を表すクラス"""
    
    def __init__(
        self, 
        game_state: WataruToGame, 
        parent: Optional['MCTSNode'] = None,
        move: Optional[Move] = None
    ):
        """
        Args:
            game_state: このノードのゲーム状態
            parent: 親ノード
            move: 親からこのノードへの手
        """
        self.game_state = game_state
        self.parent = parent
        self.move = move  # 親からこのノードへの手
        
        self.children: List['MCTSNode'] = []
        self.untried_moves: List[Move] = game_state.get_legal_moves()
        
        # 統計
        self.visits = 0
        self.wins = 0.0  # このノードから見た勝利数
        self.player = game_state.current_player  # このノードのプレイヤー
    
    def is_fully_expanded(self) -> bool:
        """すべての子ノードが展開されているか"""
        return len(self.untried_moves) == 0
    
    def is_terminal(self) -> bool:
        """終端ノード（ゲーム終了）か"""
        return self.game_state.winner is not None
    
    def ucb1(self, exploration_weight: float = 1.41) -> float:
        """
        UCB1スコアを計算
        
        Args:
            exploration_weight: 探索の重み（通常は√2 ≈ 1.41）
        
        Returns:
            UCB1スコア
        """
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = exploration_weight * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        
        return exploitation + exploration
    
    def select_child(self) -> 'MCTSNode':
        """UCB1スコアが最大の子ノードを選択"""
        return max(self.children, key=lambda child: child.ucb1())
    
    def expand(self) -> 'MCTSNode':
        """
        未展開の手を1つ選んで子ノードを作成
        
        Returns:
            新しく作成された子ノード
        """
        if not self.untried_moves:
            raise ValueError("No untried moves to expand")
        
        # ランダムに未試行の手を選択
        move = self.untried_moves.pop(random.randint(0, len(self.untried_moves) - 1))
        
        # 新しいゲーム状態を作成
        new_state = self.game_state.clone()
        new_state.apply_move(move)
        
        # 子ノードを作成
        child = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child)
        
        return child
    
    def backpropagate(self, result: float):
        """
        シミュレーション結果を親ノードに伝播
        
        Args:
            result: 勝利=1.0, 引き分け=0.5, 敗北=0.0
        """
        self.visits += 1
        self.wins += result
        
        if self.parent:
            # 親視点では結果が反転
            self.parent.backpropagate(1.0 - result)


class MCTS:
    """モンテカルロ木探索エンジン"""
    
    def __init__(
        self,
        exploration_weight: float = 1.41,
        time_limit: float = 15.0,
        max_simulations: Optional[int] = None,
        verbose: bool = False
    ):
        """
        Args:
            exploration_weight: UCB1の探索パラメータ
            time_limit: 探索時間制限（秒）
            max_simulations: 最大シミュレーション回数（Noneなら時間制限のみ）
            verbose: デバッグ情報を出力するか
        """
        self.exploration_weight = exploration_weight
        self.time_limit = time_limit
        self.max_simulations = max_simulations
        self.verbose = verbose
        self.stats = MCTSStats()
    
    def search(self, game_state: WataruToGame) -> Optional[Move]:
        """
        MCTSで最良の手を探索
        
        Args:
            game_state: 現在のゲーム状態
        
        Returns:
            最良の手（合法手がない場合はNone）
        """
        start_time = time.time()
        self.stats = MCTSStats()
        
        # ルートノードを作成
        root = MCTSNode(game_state.clone())
        
        # 合法手がない場合
        if not root.untried_moves and not root.children:
            return None
        
        # シミュレーション回数をカウント
        simulation_count = 0
        
        # 時間制限またはシミュレーション回数制限まで実行
        while True:
            # 時間制限チェック
            if time.time() - start_time > self.time_limit:
                break
            
            # シミュレーション回数制限チェック
            if self.max_simulations and simulation_count >= self.max_simulations:
                break
            
            # 1回のシミュレーション
            self._simulate_once(root)
            simulation_count += 1
        
        # 統計情報を更新
        self.stats.simulations_run = simulation_count
        self.stats.time_elapsed = time.time() - start_time
        self.stats.nodes_explored = self._count_nodes(root)
        
        # 最も訪問回数が多い子ノードを選択
        if not root.children:
            return None
        
        best_child = max(root.children, key=lambda child: child.visits)
        self.stats.best_move_visits = best_child.visits
        self.stats.best_move_win_rate = best_child.wins / best_child.visits if best_child.visits > 0 else 0.0
        
        if self.verbose:
            self._print_stats(root)
        
        return best_child.move
    
    def _simulate_once(self, root: MCTSNode):
        """1回のシミュレーションを実行"""
        
        # 1. Selection: UCB1で葉ノードまで選択
        node = root
        while not node.is_terminal() and node.is_fully_expanded() and node.children:
            node = node.select_child()
        
        # 2. Expansion: 未展開のノードがあれば展開
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()
        
        # 3. Simulation: ランダムプレイアウト
        result = self._simulate_random_playout(node.game_state.clone())
        
        # 4. Backpropagation: 結果を伝播
        # resultは勝者視点（1=勝利, -1=敗北, 0=引き分け）
        # ノード視点の結果に変換
        if result == node.player:
            node_result = 1.0  # 勝利
        elif result == 0:
            node_result = 0.5  # 引き分け
        else:
            node_result = 0.0  # 敗北
        
        node.backpropagate(node_result)
    
    def _simulate_random_playout(self, game_state: WataruToGame) -> int:
        """
        ランダムプレイアウトを実行
        
        Args:
            game_state: シミュレーション開始状態
        
        Returns:
            勝者（1, -1, 0=引き分け）
        """
        max_moves = 100  # 無限ループ防止
        move_count = 0
        
        while game_state.winner is None and move_count < max_moves:
            legal_moves = game_state.get_legal_moves()
            
            if not legal_moves:
                break
            
            # ランダムに手を選択
            move = random.choice(legal_moves)
            game_state.apply_move(move)
            move_count += 1
        
        # 勝者を返す
        if game_state.winner is None:
            return 0  # 引き分け（タイムアウト）
        
        return game_state.winner
    
    def _count_nodes(self, node: MCTSNode) -> int:
        """探索木のノード数をカウント"""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count
    
    def _print_stats(self, root: MCTSNode):
        """統計情報を出力"""
        print("\n" + "=" * 60)
        print("MCTS統計情報")
        print("=" * 60)
        print(f"シミュレーション回数: {self.stats.simulations_run}")
        print(f"探索ノード数: {self.stats.nodes_explored}")
        print(f"探索時間: {self.stats.time_elapsed:.2f}秒")
        print(f"シミュレーション/秒: {self.stats.simulations_run / self.stats.time_elapsed:.1f}")
        print(f"\n最良手の訪問回数: {self.stats.best_move_visits}")
        print(f"最良手の勝率: {self.stats.best_move_win_rate * 100:.1f}%")
        
        # トップ5の候補手を表示
        print("\nトップ5候補手:")
        sorted_children = sorted(root.children, key=lambda c: c.visits, reverse=True)
        for i, child in enumerate(sorted_children[:5], 1):
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            print(f"  {i}. 訪問: {child.visits:4d}  勝率: {win_rate*100:5.1f}%  "
                  f"手: {child.move}")
        print("=" * 60 + "\n")


# デフォルトのMCTSエンジンを作成
def create_mcts_engine(
    time_limit: float = 10.0,
    exploration_weight: float = 1.41,
    verbose: bool = True
) -> MCTS:
    """
    MCTSエンジンを作成するヘルパー関数
    
    Args:
        time_limit: 探索時間制限（秒）
        exploration_weight: 探索パラメータ
        verbose: デバッグ情報を出力するか
    
    Returns:
        MCTSエンジンインスタンス
    """
    return MCTS(
        exploration_weight=exploration_weight,
        time_limit=time_limit,
        verbose=verbose
    )