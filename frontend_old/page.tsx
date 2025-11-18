"use client";

import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { WataruToGame } from "../utils/gameLogic";
import { RandomAI } from "../utils/randomAI";
import { Move } from "../types/game";

export default function Home() {
  // ゲームロジック管理用のインスタンス
  const gameRef = useRef<WataruToGame>(new WataruToGame());

  const [currentPlayer, setCurrentPlayer] = useState<1 | -1>(1);
  // board[row][col] = [layer1, layer2] (0: 空, 1: 水色, -1: ピンク)
  const [board, setBoard] = useState<number[][][]>(
    Array.from({ length: 18 }, () => 
      Array.from({ length: 18 }, () => [0, 0])
    )
  );
  const [currentPath, setCurrentPath] = useState<{ row: number, col: number, layer: number }[]>([]); // 現在置いてる途中の座標

  // プレイヤーによって管理するブロック残数
  const [playerBlocks, setPlayerBlocks] = useState({
    1: { size4: 1, size5: 1 },   // 水色プレイヤー
    [-1]: { size4: 1, size5: 1 }, // ピンクプレイヤー
  });

  // AI対戦モード関連の状態
  const [gameMode, setGameMode] = useState<'pvp' | 'vsRandom'>('pvp');
  const [aiPlayer, setAiPlayer] = useState<1 | -1 | null>(null);
  const [isAIThinking, setIsAIThinking] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);

  // Alpha Zero用のデータ取得関数（デバッグ・将来の統合用）
  const exportGameStateForAI = () => {
    return {
      tensorBoard: gameRef.current.getBoardAsTensor(),
      gameState: gameRef.current.getStateForAI(),
      gameRecord: gameRef.current.exportGameRecord(),
    };
  };

  // moveを盤面に適用する関数
  const applyMoveToBoard = (move: Move) => {
    const newBoard = board.map(r => r.map(c => [...c]));
    move.path.forEach(({ row, col, layer }) => {
      newBoard[row][col][layer] = move.player;
    });
    setBoard(newBoard);
    
    // ブロック数を減らす
    if (move.path.length === 4) {
      setPlayerBlocks(prev => ({
        ...prev,
        [move.player]: {
          ...prev[move.player],
          size4: prev[move.player].size4 - 1
        }
      }));
    } else if (move.path.length === 5) {
      setPlayerBlocks(prev => ({
        ...prev,
        [move.player]: {
          ...prev[move.player],
          size5: prev[move.player].size5 - 1
        }
      }));
    }
    
    // 勝敗判定
    if (checkBridge(newBoard, move.player)) {
      setIsGameOver(true);
      setTimeout(() => {
        alert(`${move.player === 1 ? '水色' : 'ピンク'}の勝ちです！`);
        console.log("Game Record:", gameRef.current.exportGameRecord());
      }, 100);
      return; // ゲーム終了時はターン交代しない
    }
    
    // ターン交代
    setCurrentPlayer((-move.player) as 1 | -1);
  };

  // AIのターンを実行
  const executeAIMove = async () => {
    if (currentPlayer !== aiPlayer || isAIThinking || currentPath.length > 0 || isGameOver) return;
    
    setIsAIThinking(true);
    
    // 少し待つ（人間らしく見せる）
    await new Promise(resolve => setTimeout(resolve, 500));
    
    try {
      const game = new WataruToGame({
        board: JSON.parse(JSON.stringify(board)),
        currentPlayer,
        playerBlocks: JSON.parse(JSON.stringify(playerBlocks)),
        moveHistory: [],
      });

      const ai = new RandomAI(currentPlayer);
      const move = ai.selectMove(game);

      if (move) {
        // ゲームロジックに記録
        gameRef.current.applyMove(move);
        // UIに反映
        applyMoveToBoard(move);
      } else {
        alert("AIが手を見つけられませんでした");
      }
    } catch (error) {
      console.error("AI Error:", error);
    } finally {
      setIsAIThinking(false);
    }
  };

  // AIのターンになったら自動実行
  useEffect(() => {
    if (currentPlayer === aiPlayer && gameMode === 'vsRandom' && !isAIThinking && !isGameOver) {
      executeAIMove();
    }
  }, [currentPlayer, aiPlayer, gameMode, isAIThinking, isGameOver]);

  const handleCellClick = (row: number, col: number) => {
    // AI対戦中は人間のターンでのみクリック可能
    if (gameMode === 'vsRandom' && currentPlayer === aiPlayer) return;
    if (isAIThinking) return;
    if (isGameOver) return;
    const layers = board[row][col];
    const layer1 = layers[0];
    const layer2 = layers[1];
    
    // レイヤー2が既に埋まっている場合は置けない
    if (layer2 !== 0) return;
    
    // 起点の場合
    if (currentPath.length === 0) {
      let targetLayer = -1;
      
      // レイヤー1が空なら、レイヤー1に置く
      if (layer1 === 0) {
        targetLayer = 0;
      } 
      // レイヤー1に自分の色があり、レイヤー2が空なら、レイヤー2に置ける（橋の起点）
      else if (layer1 === currentPlayer) {
        targetLayer = 1;
      }
      // それ以外は置けない
      else {
        return;
      }
      
      setCurrentPath([{ row, col, layer: targetLayer }]);
      const newBoard = board.map(r => r.map(c => [...c]));
      newBoard[row][col][targetLayer] = currentPlayer;
      setBoard(newBoard);
      return;
    }
    
    // 2マス目以降の処理
    const firstLayer = currentPath[0].layer;
    let targetLayer = -1;
    
    if (firstLayer === 0) {
      // レイヤー1モード：レイヤー1が空でなければならない
      if (layer1 === 0) {
        targetLayer = 0;
      } else {
        return; // レイヤー1に何かある場合は置けない
      }
    } else {
      // レイヤー2モード（橋渡し）
      if (layer1 === currentPlayer) {
        // レイヤー1に自分の色がある場合：レイヤー2に置く（既存マス）
        targetLayer = 1;
      } else if (layer1 === 0) {
        // レイヤー1が空の場合：レイヤー2に置く（新規マス）
        targetLayer = 1;
      } else {
        // レイヤー1に相手の色がある場合は置けない
        return;
      }
    }
    
    // すでに置いている場合、currentPath内のいずれかのマスの隣でなければ無視
    const isAdjacentToPath = currentPath.some(p => 
      (Math.abs(p.row - row) === 1 && p.col === col) ||
      (Math.abs(p.col - col) === 1 && p.row === row)
    );
    
    if (!isAdjacentToPath) return;
    
    // すでにcurrentPathに含まれていたら無視（重複防止）
    if (currentPath.some(p => p.row === row && p.col === col)) return;
    
    // 一直線チェック：2マス目以降は方向を決定し、その方向に沿っているか確認
    if (currentPath.length >= 1) {
      const newPath = [...currentPath, { row, col, layer: targetLayer }];
      
      // すべてのマスが同じ行または同じ列にあるかチェック
      const allSameRow = newPath.every(p => p.row === newPath[0].row);
      const allSameCol = newPath.every(p => p.col === newPath[0].col);
      
      if (!allSameRow && !allSameCol) return; // 一直線でない場合は無視
    }
    
    //6マス目は無視
    if (currentPath.length === 5) return;
    
    // 新しいマスを追加
    const newPath = [...currentPath, { row, col, layer: targetLayer }];
    setCurrentPath(newPath);

    const newBoard = board.map(r => r.map(c => [...c]));
    newBoard[row][col][targetLayer] = currentPlayer;
    setBoard(newBoard);
  };

 

  const handleCancel = () => {
    // currentPathに置いたマスをボードから削除
    const newBoard = board.map(r => r.map(c => [...c]));
    currentPath.forEach(({ row, col, layer }) => {
      newBoard[row][col][layer] = 0;
    });
    setBoard(newBoard);
    setCurrentPath([]);
  };

  const handleReset = () => {
    // ゲームロジックインスタンスもリセット
    gameRef.current = new WataruToGame();
    
    setBoard(Array.from({ length: 18 }, () => 
      Array.from({ length: 18 }, () => [0, 0])
    ));
    setCurrentPlayer(1);
    setCurrentPath([]);
    setPlayerBlocks({ 1: { size4: 1, size5: 1 }, [-1]: { size4: 1, size5: 1 } });
    setIsAIThinking(false);
    setIsGameOver(false);
  };

  function checkBridge(board: number[][][], player: 1 | -1) {
    const n = board.length; // 盤面のサイズ（例: 18）
    const visited = Array.from({ length: n }, () => Array(n).fill(false));
    const stack: { row: number; col: number }[] = [];
    
    // マスにプレイヤーの色があるかチェック（レイヤー1またはレイヤー2）
    const hasPlayerColor = (row: number, col: number) => {
      return board[row][col][0] === player || board[row][col][1] === player;
    };
  
    // 🌱 スタート地点を探す
    if (player === 1) {
      // 水色は上の端
      for (let col = 0; col < n; col++) {
        if (hasPlayerColor(0, col)) {
          stack.push({ row: 0, col }); // スタート候補として追加
          visited[0][col] = true; // 一度見た場所として記録
        }
      }
    } else {
      // ピンクは左の端
      for (let row = 0; row < n; row++) {
        if (hasPlayerColor(row, 0)) {
          stack.push({ row, col: 0 });
          visited[row][0] = true;
        }
      }
    }
  
    // 🔁 隣（上下左右）に同じ色があるかを探索する
    const directions = [
      { dr: 1, dc: 0 }, // 下
      { dr: -1, dc: 0 }, // 上
      { dr: 0, dc: 1 }, // 右
      { dr: 0, dc: -1 }, // 左
    ];
  
    // 🚶 探索開始！
    while (stack.length > 0) {
      const current = stack.pop();
      if (!current) continue;
      const { row, col } = current;
  
      // 🎯 もし反対側まで届いたら勝ち！
      if (player === 1 && row === n - 1) return true; // 水色：下まで
      if (player === -1 && col === n - 1) return true; // ピンク：右まで
  
      // 🔍 周り4方向を確認する
      for (const { dr, dc } of directions) {
        const nr: number = row + dr;
        const nc: number = col + dc;
        if (
          nr >= 0 && nr < n && nc >= 0 && nc < n && // 盤面外チェック
          !visited[nr][nc] && // まだ見ていない
          hasPlayerColor(nr, nc) // 自分の色
        ) {
          visited[nr][nc] = true; // 見た記録を残す
          stack.push({ row: nr, col: nc }); // 次の探索候補として追加
        }
      }
    }
  
    // 🚫 最後まで見ても反対側に届かなかった
    return false;
  }

  const handleConfirm = () => {
    if (currentPath.length < 3) return; // 3マス未満は確定できない
    if (isGameOver) return; // ゲーム終了後は確定不可
    
    // レイヤー2モード（橋渡し）の場合、始点と終点が両方とも既存マスでなければならない
    const firstCell = currentPath[0];
    const lastCell = currentPath[currentPath.length - 1];
    
    if (firstCell.layer === 1) {
      // 始点がレイヤー2の場合
      const firstCellLayers = board[firstCell.row][firstCell.col];
      const lastCellLayers = board[lastCell.row][lastCell.col];
      
      // 終点もレイヤー2で、かつレイヤー1に自分の色がなければならない
      if (lastCell.layer !== 1 || lastCellLayers[0] !== currentPlayer) {
        return alert("橋渡しの終点は既存のマスでなければなりません");
      }
    }
    
    // 4マス・5マスの場合、それぞれのブロック在庫が0なら確定不可
    if (currentPath.length === 4 && playerBlocks[currentPlayer].size4 === 0) return alert("4マスブロックはもうありません");
    if (currentPath.length === 5 && playerBlocks[currentPlayer].size5 === 0) return alert("5マスブロックはもうありません");
    
    // ゲームロジックに手を記録
    const move = {
      player: currentPlayer,
      path: currentPath,
      timestamp: Date.now(),
    };
    gameRef.current.applyMove(move);
    
    // ブロックを減らす
    if (currentPath.length === 4) {
      // 4マスブロックを使用
      setPlayerBlocks(prev => ({ 
        ...prev, 
        [currentPlayer]: { 
          ...prev[currentPlayer], 
          size4: prev[currentPlayer].size4 - 1 
        } 
      }));
    } else if (currentPath.length === 5) {
      // 5マスブロックを使用
      setPlayerBlocks(prev => ({ 
        ...prev, 
        [currentPlayer]: { 
          ...prev[currentPlayer], 
          size5: prev[currentPlayer].size5 - 1 
        } 
      }));
    }
    
    // 勝敗判定
    if (checkBridge(board, currentPlayer)) {
      alert("あなたの勝ちです！");
      // デバッグ用：ゲーム記録を出力
      console.log("Game Record:", gameRef.current.exportGameRecord());
    }
    
    // currentPathをクリアしてターンを移動
    setCurrentPath([]);
    setCurrentPlayer((-currentPlayer) as 1 | -1);
  };

  return (
    <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
      {/* 左サイド - 水色プレイヤー */}
      <div className="flex-1 border-r-2 border-gray-300 flex flex-col items-center justify-center gap-8">
        {currentPlayer === 1 && (
          <div className="text-2xl font-bold text-cyan-400">
            あなたの番です
          </div>
        )}
        
        {/* ブロック表示 */}
        <div className="flex flex-col gap-4">
          {/* 3マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
            </div>
            <span className="text-lg font-bold text-black">∞</span>
          </div>
          
          {/* 4マスブロック */}
          <div className={`flex items-center gap-3 ${playerBlocks[1].size4 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              <div className={`w-5 h-5 border ${playerBlocks[1].size4 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size4 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size4 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size4 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
            </div>
            <span className="text-lg font-bold text-black">残{playerBlocks[1].size4}</span>
          </div>
          
          {/* 5マスブロック */}
          <div className={`flex items-center gap-3 ${playerBlocks[1].size5 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              <div className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
            </div>
            <span className="text-lg font-bold text-black">残{playerBlocks[1].size5}</span>
          </div>
        </div>
      </div>
      
      {/* メイン画面（中央） */}
      <div className="flex-1 flex flex-col items-center border-r-2 border-gray-300 py-8">
        {/* タイトル */}
        <div className="mb-4">
          <h1 className="text-4xl font-bold">
            <span className="text-cyan-400">ワタルート</span>
            <span className="text-pink-400">道場</span>
          </h1>
        </div>
        
        {/* ゲームモード選択 */}
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => {
              setGameMode('pvp');
              setAiPlayer(null);
              handleReset();
            }}
            className={`px-4 py-2 rounded font-bold transition ${
              gameMode === 'pvp' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            }`}
          >
            対人戦
          </button>
          <button
            onClick={() => {
              setGameMode('vsRandom');
              setAiPlayer(-1); // ピンクをAIに
              handleReset();
            }}
            className={`px-4 py-2 rounded font-bold transition ${
              gameMode === 'vsRandom' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            }`}
          >
            vsランダムAI
          </button>
        </div>

        {/* AI思考中の表示 */}
        {isAIThinking && (
          <div className="mb-2 text-lg font-bold text-purple-600 animate-pulse">
            🤔 AIが考え中...
          </div>
        )}
        
        {/* タイル配置中なら表示 */}
        <div className="flex justify-center items-center mt-4 mb-6 min-h-[56px]">
          {currentPath.length > 0 ? (
            <div className="flex gap-4 mt-2">
              {currentPath.length > 2 && (
                <button
                  onClick={handleConfirm}
                  className="px-4 py-1 bg-cyan-600 text-white font-bold rounded hover:bg-cyan-700 transition"
                >
                  確定
                </button>
              )}
              <button
                onClick={handleCancel}
                className="px-4 py-1 bg-gray-500 text-white font-bold rounded hover:bg-gray-600 transition"
              >
                キャンセル
              </button>
            </div>
          ) : (
            <div className="flex gap-4 mt-2" />
          )}
        </div>
        {/* 18x18の盤面 */}
        <div className="grid grid-cols-18 gap-0 border-t-4 border-b-4 border-l-4 border-r-4 border-t-cyan-400 border-b-cyan-400 border-l-pink-400 border-r-pink-400">
          {Array.from({ length: 18 * 18 }).map((_, index) => {
            const row = Math.floor(index / 18);
            const col = index % 18;
            const layers = board[row][col];
            const layer1 = layers[0];
            const layer2 = layers[1];
            
            // レイヤー2が優先表示（上に重なっている）
            let bgColor = "bg-black";
            if (layer2 !== 0) {
              // レイヤー2がある場合は明るい色で表示
              bgColor = layer2 === 1 ? "bg-cyan-200" : "bg-pink-200";
            } else if (layer1 !== 0) {
              // レイヤー1のみの場合は通常の色
              bgColor = layer1 === 1 ? "bg-cyan-400" : "bg-pink-400";
            }
            
            return (
              <div
                key={index}
                onClick={() => handleCellClick(row, col)}
                className={`w-6 h-6 ${bgColor} border border-gray-600 cursor-pointer hover:opacity-80 transition-all`}
              ></div>
            );
          })}
        </div>
        
        {/* リセットボタン */}
        <button
          onClick={handleReset}
          className="mt-6 px-6 py-2 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 transition-colors"
        >
          リセット
        </button>
      </div>
      
      {/* 右サイド - ピンクプレイヤー */}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        {currentPlayer === -1 && (
          <div className="text-2xl font-bold text-pink-400">
            あなたの番です
          </div>
        )}
        
        {/* ブロック表示 */}
        <div className="flex flex-col gap-4">
          {/* 3マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
            </div>
            <span className="text-lg font-bold text-black">∞</span>
          </div>
          
          {/* 4マスブロック */}
          <div className={`flex items-center gap-3 ${playerBlocks[-1].size4 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              <div className={`w-5 h-5 border ${playerBlocks[-1].size4 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size4 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size4 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size4 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
            </div>
            <span className="text-lg font-bold text-black">残{playerBlocks[-1].size4}</span>
          </div>
          
          {/* 5マスブロック */}
          <div className={`flex items-center gap-3 ${playerBlocks[-1].size5 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              <div className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              <div className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
            </div>
            <span className="text-lg font-bold text-black">残{playerBlocks[-1].size5}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
