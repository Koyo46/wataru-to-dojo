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


def visualize_board(game_state: WataruToGame, title: str = "盤面状態") -> str:
    """
    ゲーム盤面を視覚化して文字列として返す
    
    Args:
        game_state: 表示するゲーム状態
        title: 表示タイトル
    
    Returns:
        視覚化された盤面の文字列
    """
    board = game_state.board.board
    size = len(board)
    
    # 色の記号
    symbols = {
        0: '·',   # 空
        1: '🔵',  # 水色 (プレイヤー1)
        -1: '🔴', # ピンク (プレイヤー-1)
    }
    
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"{title}")
    lines.append(f"{'='*60}")
    
    # レイヤー1
    lines.append("【レイヤー1】")
    lines.append("    " + "".join(f"{i:2d}" for i in range(min(10, size))))
    for row in range(size):
        layer1_cells = [symbols[board[row][col][0]] for col in range(size)]
        lines.append(f"{row:2d}: " + " ".join(layer1_cells))
    
    # レイヤー2（何か置かれている場合のみ）
    has_layer2 = any(board[row][col][1] != 0 for row in range(size) for col in range(size))
    if has_layer2:
        lines.append("\n【レイヤー2】")
        lines.append("    " + "".join(f"{i:2d}" for i in range(min(10, size))))
        for row in range(size):
            layer2_cells = [symbols[board[row][col][1]] for col in range(size)]
            lines.append(f"{row:2d}: " + " ".join(layer2_cells))
    
    # ゲーム情報
    current_player_name = "水色🔵" if game_state.current_player == 1 else "ピンク🔴"
    lines.append(f"\n現在のプレイヤー: {current_player_name}")
    lines.append(f"手数: {len(game_state.move_history)}")
    
    if game_state.winner is not None:
        if game_state.winner == 0:
            lines.append("結果: 引き分け")
        else:
            winner_name = "水色🔵" if game_state.winner == 1 else "ピンク🔴"
            lines.append(f"勝者: {winner_name}")
    
    lines.append(f"{'='*60}\n")
    
    return "\n".join(lines)


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
        verbose: bool = False,
        use_tactical_heuristics: bool = True,
        debug_playout: bool = False,
        debug_playout_count: int = 1
    ):
        """
        Args:
            exploration_weight: UCB1の探索パラメータ
            time_limit: 探索時間制限（秒）
            max_simulations: 最大シミュレーション回数（Noneなら時間制限のみ）
            verbose: デバッグ情報を出力するか
            use_tactical_heuristics: 戦術的ヒューリスティックを使用するか
                True: Tactical MCTS（勝利手検出・防御あり）
                False: Pure MCTS（完全ランダムプレイアウト）
            debug_playout: プレイアウトのデバッグ情報を表示するか
            debug_playout_count: デバッグ表示するプレイアウトの回数
        """
        self.exploration_weight = exploration_weight
        self.time_limit = time_limit
        self.max_simulations = max_simulations
        self.verbose = verbose
        self.use_tactical_heuristics = use_tactical_heuristics
        self.debug_playout = debug_playout
        self.debug_playout_count = debug_playout_count
        self.stats = MCTSStats()
        self._simulation_count = 0  # 現在のシミュレーション回数
    
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
        self._simulation_count = 0  # リセット
        
        # ルートノードを作成
        root = MCTSNode(game_state.clone())
        
        # 合法手がない場合
        if not root.untried_moves and not root.children:
            return None
        
        # Tactical MCTSモードの場合、王手への即座の対応
        if self.use_tactical_heuristics:
            current_player = game_state.current_player
            opponent = -current_player
            test_game = game_state.clone()
            test_game.current_player = opponent
            opponent_moves = test_game.get_legal_moves()
            
            # 相手の勝利手をチェック
            has_opponent_winning_move = False
            opponent_winning_moves = []
            for opp_move in opponent_moves:
                test_game2 = test_game.clone()
                test_game2.apply_move(opp_move)
                if test_game2.winner == opponent:
                    has_opponent_winning_move = True
                    opponent_winning_moves.append(opp_move)
            
            # 王手がある場合、即座に防御手を探して返す
            if has_opponent_winning_move:
                opponent_name = "水色" if opponent == 1 else "ピンク"
                current_name = "水色" if current_player == 1 else "ピンク"
                print(f"\n{'='*60}")
                print(f"[緊急王手] {opponent_name}が{current_name}に王手！")
                print(f"[危険度] 相手の勝利手: {len(opponent_winning_moves)}通り")
                print(f"[即応] 防御手を優先的に選択します")
                print(f"{'='*60}\n")
                
                # 防御手を探す（verboseはFalse、すでに上で出力済み）
                legal_moves = game_state.get_legal_moves()
                blocking_move = self._find_blocking_move(game_state, legal_moves, verbose=False)
                
                if blocking_move:
                    print(f"[防御選択] {blocking_move}")
                    print(f"{'='*60}\n")
                    
                    # 統計情報を簡易的に設定
                    self.stats.simulations_run = 0
                    self.stats.time_elapsed = time.time() - start_time
                    self.stats.nodes_explored = 1
                    self.stats.best_move_visits = 1
                    self.stats.best_move_win_rate = 1.0
                    
                    if self.verbose:
                        print("=" * 60)
                        print("防御手を即座に選択（探索スキップ）")
                        print("=" * 60 + "\n")
                    
                    return blocking_move
                else:
                    print(f"[詰み確定] 防御不可能、最善手を探索します")
                    print(f"{'='*60}\n")
        
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
        
        # デバッグモードチェック
        should_debug = self.debug_playout and self._simulation_count < self.debug_playout_count
        
        if should_debug:
            print(f"\n{'#'*60}")
            print(f"# シミュレーション {self._simulation_count + 1}/{self.debug_playout_count}")
            print(f"{'#'*60}")
        
        # 1. Selection: UCB1で葉ノードまで選択
        node = root
        selection_depth = 0
        while not node.is_terminal() and node.is_fully_expanded() and node.children:
            node = node.select_child()
            selection_depth += 1
        
        if should_debug:
            print(f"\n[Selection] 深さ {selection_depth} のノードまで選択")
        
        # 2. Expansion: 未展開のノードがあれば展開
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()
            if should_debug:
                print(f"[Expansion] 新しいノードを展開: {node.move}")
        
        # 3. Simulation: ランダムプレイアウト
        result = self._simulate_random_playout(node.game_state.clone(), debug=should_debug)
        
        # 4. Backpropagation: 結果を伝播
        # resultは勝者視点（1=勝利, -1=敗北, 0=引き分け）
        # ノード視点の結果に変換
        if result == node.player:
            node_result = 1.0  # 勝利
        elif result == 0:
            node_result = 0.5  # 引き分け
        else:
            node_result = 0.0  # 敗北
        
        if should_debug:
            result_str = "勝利" if node_result == 1.0 else "引き分け" if node_result == 0.5 else "敗北"
            winner_name = "水色🔵" if result == 1 else "ピンク🔴" if result == -1 else "引き分け"
            print(f"\n[Backpropagation] プレイアウト結果: {winner_name} (ノード視点: {result_str})")
            print(f"{'#'*60}\n")
        
        node.backpropagate(node_result)
        self._simulation_count += 1
    
    def _find_winning_move(self, game_state: WataruToGame, legal_moves: List[Move], max_check: int = 30) -> Optional[Move]:
        """
        即座に勝てる手を探す
        
        最適化: 最初のN手だけチェック
        
        Args:
            game_state: 現在のゲーム状態
            legal_moves: 合法手のリスト
            max_check: チェックする最大手数（デフォルト: 30）
        
        Returns:
            勝利手があればその手、なければNone
        """
        current_player = game_state.current_player
        check_count = min(max_check, len(legal_moves))
        
        for i in range(check_count):
            move = legal_moves[i]
            # 手を試す
            test_game = game_state.clone()
            test_game.apply_move(move)
            
            # 勝利判定
            if test_game.winner == current_player:
                return move
        
        return None
    
    def _find_blocking_move(self, game_state: WataruToGame, legal_moves: List[Move], verbose: bool = False) -> Optional[Move]:
        """
        相手の勝利手を防ぐ手を探す（効率的版）
        
        戦略:
        1. 相手に即座の勝利手があるかチェック
        2. ある場合、自分の各手を試して相手の勝利手を防げるかチェック
        3. 防げる手があればそれを返す
        
        Args:
            game_state: 現在のゲーム状態
            legal_moves: 合法手のリスト
            verbose: デバッグ情報を出力するか（デフォルト: False）
        
        Returns:
            防御手があればその手、なければNone
        """
        current_player = game_state.current_player
        opponent = -current_player
        
        # まず、現在の状態で相手に勝利手があるかチェック
        test_game = game_state.clone()
        test_game.current_player = opponent
        
        opponent_moves = test_game.get_legal_moves()
        has_opponent_winning_move = False
        winning_moves_list = []
        
        for opp_move in opponent_moves:
            test_game2 = test_game.clone()
            test_game2.apply_move(opp_move)
            
            if test_game2.winner == opponent:
                has_opponent_winning_move = True
                winning_moves_list.append(opp_move)
        
        # 相手に勝利手がない場合は防御不要
        if not has_opponent_winning_move:
            return None
        
        # 王手を検知！コンソールに表示（verboseモードの場合のみ）
        if verbose:
            opponent_name = "水色" if opponent == 1 else "ピンク"
            current_name = "水色" if current_player == 1 else "ピンク"
            print(f"\n{'='*60}")
            print(f"[王手検知] {opponent_name}が王手をかけています！")
            print(f"[ピンチ] {current_name}は防御が必要です！")
            print(f"[危険] 相手の勝利手: {len(winning_moves_list)}通り")
            print(f"{'='*60}\n")
        
        # 相手に勝利手がある場合、それを防ぐ手を探す
        # 各自分の手を試して、その後相手が勝てなくなるかチェック
        for my_move in legal_moves:
            test_game = game_state.clone()
            test_game.apply_move(my_move)
            
            # この手を打った後、相手に勝利手があるかチェック
            opponent_moves_after = test_game.get_legal_moves()
            opponent_can_still_win = False
            
            for opp_move in opponent_moves_after:
                test_game2 = test_game.clone()
                test_game2.apply_move(opp_move)
                
                if test_game2.winner == opponent:
                    opponent_can_still_win = True
                    break
            
            # この手で相手の勝利を防げる
            if not opponent_can_still_win:
                if verbose:
                    print(f"[防御成功] 防御手を発見: {my_move}")
                    print(f"{'='*60}\n")
                return my_move
        
        # すべての手で相手が勝ってしまう場合はNone
        # （詰んでいる状態）
        if verbose:
            print(f"[詰み] 防御不可能！すべての手で相手が勝利します")
            print(f"{'='*60}\n")
        return None
    
    def _simulate_pure_random_playout(self, game_state: WataruToGame, debug: bool = False) -> int:
        """
        Pure MCTSモード: 完全ランダムプレイアウト
        
        Args:
            game_state: シミュレーション開始状態
            debug: デバッグ情報を出力するか
        
        Returns:
            勝者（1, -1, 0=引き分け）
        """
        max_moves = 100  # 無限ループ防止
        move_count = 0
        
        if debug:
            print(visualize_board(game_state, f"プレイアウト開始 (Pure Random)"))
        
        while game_state.winner is None and move_count < max_moves:
            legal_moves = game_state.get_legal_moves()
            
            if not legal_moves:
                break
            
            # 完全ランダムに選択
            move = random.choice(legal_moves)
            
            if debug:
                player_name = "水色🔵" if move.player == 1 else "ピンク🔴"
                print(f"\n[手 {move_count + 1}] {player_name} が打った手: {move}")
                print(f"  合法手の数: {len(legal_moves)}")
            
            game_state.apply_move(move)
            move_count += 1
            
            if debug and move_count % 5 == 0:  # 5手ごとに盤面表示
                print(visualize_board(game_state, f"プレイアウト途中 ({move_count}手目)"))
        
        if debug:
            print(visualize_board(game_state, f"プレイアウト終了 ({move_count}手)"))
        
        # 勝者を返す
        if game_state.winner is None:
            return 0  # 引き分け（タイムアウト）
        
        return game_state.winner
    
    def _has_immediate_threat(self, game_state: WataruToGame, max_check: int = 10) -> bool:
        """
        即座の脅威（王手）があるかを高速チェック
        
        最適化: 最初のN手だけチェックして早期リターン
        
        Args:
            game_state: 現在のゲーム状態
            max_check: チェックする最大手数（デフォルト: 50）
        
        Returns:
            相手に勝利手がある場合True
        """
        current_player = game_state.current_player
        opponent = -current_player
        
        # 相手のターンをシミュレート
        test_game = game_state.clone()
        test_game.current_player = opponent
        opponent_moves = test_game.get_legal_moves()
        
        # 最初のN手だけチェック（高速化）
        check_count = min(max_check, len(opponent_moves))
        
        for i in range(check_count):
            opp_move = opponent_moves[i]
            test_game2 = test_game.clone()
            test_game2.apply_move(opp_move)
            if test_game2.winner == opponent:
                return True
        
        return False
    
    def _simulate_tactical_playout(self, game_state: WataruToGame, debug: bool = False) -> int:
        """
        Tactical MCTSモード: 戦術的ヒューリスティック付きプレイアウト
        
        最適化版:
        - 勝利手のチェックのみ実行（超高速）
        - 防御チェックは重いのでプレイアウト中はスキップ
        - 代わりにルートノードでの防御判定に集中
        
        Args:
            game_state: シミュレーション開始状態
            debug: デバッグ情報を出力するか
        
        Returns:
            勝者（1, -1, 0=引き分け）
        """
        max_moves = 100  # 無限ループ防止
        move_count = 0
        
        if debug:
            print(visualize_board(game_state, f"プレイアウト開始 (Tactical)"))
        
        while game_state.winner is None and move_count < max_moves:
            legal_moves = game_state.get_legal_moves()
            
            if not legal_moves:
                break
            
            # 1. 即座に勝てる手があれば必ず打つ（高速チェック）
            winning_move = self._find_winning_move(game_state, legal_moves)
            if winning_move:
                if debug:
                    player_name = "水色🔵" if winning_move.player == 1 else "ピンク🔴"
                    print(f"\n[手 {move_count + 1}] {player_name} が勝利手を発見！: {winning_move}")
                    print(f"  合法手の数: {len(legal_moves)}")
                
                game_state.apply_move(winning_move)
                move_count += 1
                continue
            
            # 2. ランダムに選択（防御チェックはスキップして高速化）
            move = random.choice(legal_moves)
            
            if debug:
                player_name = "水色🔵" if move.player == 1 else "ピンク🔴"
                print(f"\n[手 {move_count + 1}] {player_name} が打った手: {move}")
                print(f"  合法手の数: {len(legal_moves)}")
            
            game_state.apply_move(move)
            move_count += 1
            
            if debug and move_count % 5 == 0:  # 5手ごとに盤面表示
                print(visualize_board(game_state, f"プレイアウト途中 ({move_count}手目)"))
        
        if debug:
            print(visualize_board(game_state, f"プレイアウト終了 ({move_count}手)"))
        
        # 勝者を返す
        if game_state.winner is None:
            return 0  # 引き分け（タイムアウト）
        
        return game_state.winner
    
    def _simulate_random_playout(self, game_state: WataruToGame, debug: bool = False) -> int:
        """
        ランダムプレイアウトを実行（モードに応じて切り替え）
        
        Args:
            game_state: シミュレーション開始状態
            debug: デバッグ情報を出力するか
        
        Returns:
            勝者（1, -1, 0=引き分け）
        """
        if self.use_tactical_heuristics:
            return self._simulate_tactical_playout(game_state, debug=debug)
        else:
            return self._simulate_pure_random_playout(game_state, debug=debug)
    
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
    max_simulations: Optional[int] = None,
    verbose: bool = True,
    use_tactical_heuristics: bool = True,
    debug_playout: bool = False,
    debug_playout_count: int = 1
) -> MCTS:
    """
    MCTSエンジンを作成するヘルパー関数
    
    Args:
        time_limit: 探索時間制限（秒）
        exploration_weight: 探索パラメータ
        max_simulations: 最大シミュレーション回数（Noneなら時間制限のみ）
        verbose: デバッグ情報を出力するか
        use_tactical_heuristics: 戦術的ヒューリスティックを使用するか
            True: Tactical MCTS（強い、遅い）
            False: Pure MCTS（弱い、速い）
        debug_playout: プレイアウトのデバッグ情報を表示するか
        debug_playout_count: デバッグ表示するプレイアウトの回数
    
    Returns:
        MCTSエンジンインスタンス
    """
    return MCTS(
        exploration_weight=exploration_weight,
        time_limit=time_limit,
        max_simulations=max_simulations,
        verbose=verbose,
        use_tactical_heuristics=use_tactical_heuristics,
        debug_playout=debug_playout,
        debug_playout_count=debug_playout_count
    )