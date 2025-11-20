"use client";

import { useState, useEffect } from "react";
import { apiClient, Position as APIPosition, Move as APIMove } from "../lib/api-client";

type GameMode = 'pvp' | 'vsAPI' | 'vsAlphaZero';

export default function Home() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [boardSize, setBoardSize] = useState<9 | 18>(18);
  const [currentPlayer, setCurrentPlayer] = useState<1 | -1>(1);
  const [board, setBoard] = useState<number[][][]>(
    Array.from({ length: 18 }, () => 
      Array.from({ length: 18 }, () => [0, 0])
    )
  );
  const [currentPath, setCurrentPath] = useState<{ row: number, col: number, layer: number }[]>([]);
  const [playerBlocks, setPlayerBlocks] = useState({
    1: { size4: 1, size5: 1 },
    [-1]: { size4: 1, size5: 1 },
  });
  const [gameMode, setGameMode] = useState<GameMode>('pvp');
  const [aiDifficulty, setAiDifficulty] = useState<'easy' | 'hard'>('hard');
  const [isAIThinking, setIsAIThinking] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState(false);

  // APIヘルスチェック
  useEffect(() => {
    const checkAPI = async () => {
      try {
        await apiClient.healthCheck();
        setApiConnected(true);
        console.log("✅ API接続成功");
      } catch (error) {
        setApiConnected(false);
        console.error("❌ API接続失敗:", error);
      }
    };
    checkAPI();
  }, []);

  // ゲーム初期化
  useEffect(() => {
    if (apiConnected && !gameId) {
      initializeGame();
    }
  }, [apiConnected]);

  const initializeGame = async (size?: number) => {
    setIsLoading(true);
    setErrorMessage(null);
    const gameSize = size || boardSize;
    try {
      const response = await apiClient.createNewGame(gameSize);
      setGameId(response.game_id);
      updateGameState(response.state);
      console.log("🎮 新しいゲームを作成:", response.game_id, `(${gameSize}x${gameSize})`);
    } catch (error) {
      console.error("ゲーム作成エラー:", error);
      setErrorMessage("ゲームの作成に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const updateGameState = (state: any) => {
    setBoard(state.board.board);
    setCurrentPlayer(state.current_player);
    setPlayerBlocks({
      1: state.player_blocks["1"],
      [-1]: state.player_blocks["-1"],
    });
    setIsGameOver(state.winner !== null);
  };

  // AI対戦モードでAIのターン
  useEffect(() => {
    if ((gameMode === 'vsAPI' || gameMode === 'vsAlphaZero') && currentPlayer === -1 && !isAIThinking && !isGameOver && gameId) {
      executeAIMove();
    }
  }, [currentPlayer, gameMode, isAIThinking, isGameOver, gameId]);

  const executeAIMove = async () => {
    if (!gameId) return;
    
    setIsAIThinking(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    
    try {
      // Alpha ZeroモードかMCTSモードかで分岐
      const aiResponse = gameMode === 'vsAlphaZero' 
        ? await apiClient.getAlphaZeroMove(gameId, -1)
        : await apiClient.getAIMove(gameId, -1, aiDifficulty);
      
      if (aiResponse.move) {
        const moveResponse = await apiClient.applyMove(gameId, aiResponse.move);
        
        if (moveResponse.success) {
          updateGameState(moveResponse.state);
          
          if (moveResponse.winner) {
            setTimeout(() => {
              alert(`${moveResponse.winner === 1 ? '水色' : 'ピンク'}の勝ちです！`);
            }, 100);
          }
        }
      }
    } catch (error) {
      console.error("AI手の取得エラー:", error);
      setErrorMessage("AIの手の取得に失敗しました");
    } finally {
      setIsAIThinking(false);
    }
  };

  const handleCellClick = (row: number, col: number) => {
    if ((gameMode === 'vsAPI' || gameMode === 'vsAlphaZero') && currentPlayer === -1) return;
    if (isAIThinking || isGameOver || !gameId) return;
    
    const layers = board[row][col];
    const layer1 = layers[0];
    const layer2 = layers[1];
    
    if (layer2 !== 0) return;
    
    // 起点の場合
    if (currentPath.length === 0) {
      let targetLayer = -1;
      
      if (layer1 === 0) {
        targetLayer = 0;
      } else if (layer1 === currentPlayer) {
        targetLayer = 1;
      } else {
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
      if (layer1 === 0) {
        targetLayer = 0;
      } else {
        return;
      }
    } else {
      // レイヤー2モード（橋渡し）
      if (layer1 === 0) {
        // 空白の場合は常にOK
        targetLayer = 1;
      } else if (layer1 === currentPlayer) {
        // 自分のマスの場合、3マス目以降（終点候補）のみOK
        // currentPath.length >= 2 は「起点 + 2マス目以上」なので、これから追加するのが3マス目以降
        if (currentPath.length >= 2) {
          targetLayer = 1;
        } else {
          // 2マス目（間のマス）には自分のマスがあってはダメ
          return;
        }
      } else {
        // 相手の色の場合は配置不可
        return;
      }
    }
    
    const isAdjacentToPath = currentPath.some(p => 
      (Math.abs(p.row - row) === 1 && p.col === col) ||
      (Math.abs(p.col - col) === 1 && p.row === row)
    );
    
    if (!isAdjacentToPath) return;
    if (currentPath.some(p => p.row === row && p.col === col)) return;
    
    if (currentPath.length >= 1) {
      const newPath = [...currentPath, { row, col, layer: targetLayer }];
      const allSameRow = newPath.every(p => p.row === newPath[0].row);
      const allSameCol = newPath.every(p => p.col === newPath[0].col);
      if (!allSameRow && !allSameCol) return;
    }
    
    if (currentPath.length === 5) return;
    
    const newPath = [...currentPath, { row, col, layer: targetLayer }];
    setCurrentPath(newPath);

    const newBoard = board.map(r => r.map(c => [...c]));
    newBoard[row][col][targetLayer] = currentPlayer;
    setBoard(newBoard);
  };

  const handleCancel = () => {
    const newBoard = board.map(r => r.map(c => [...c]));
    currentPath.forEach(({ row, col, layer }) => {
      newBoard[row][col][layer] = 0;
    });
    setBoard(newBoard);
    setCurrentPath([]);
  };

  const handleConfirm = async () => {
    if (currentPath.length < 3 || isGameOver || !gameId) return;
    
    const firstCell = currentPath[0];
    const lastCell = currentPath[currentPath.length - 1];
    
    if (firstCell.layer === 1) {
      const lastCellLayers = board[lastCell.row][lastCell.col];
      if (lastCell.layer !== 1 || lastCellLayers[0] !== currentPlayer) {
        return alert("橋渡しの終点は既存のマスでなければなりません");
      }
    }
    
    if (currentPath.length === 4 && playerBlocks[currentPlayer].size4 === 0) {
      return alert("4マスブロックはもうありません");
    }
    if (currentPath.length === 5 && playerBlocks[currentPlayer].size5 === 0) {
      return alert("5マスブロックはもうありません");
    }
    
    setIsLoading(true);
    setErrorMessage(null);
    
    try {
      const move: APIMove = {
        player: currentPlayer,
        path: currentPath.map(p => ({ row: p.row, col: p.col, layer: p.layer })),
        timestamp: Date.now() / 1000,
      };
      
      const response = await apiClient.applyMove(gameId, move);
      
      if (response.success) {
        updateGameState(response.state);
        setCurrentPath([]);
        
        if (response.winner) {
          setTimeout(() => {
            alert(`${response.winner === 1 ? '水色' : 'ピンク'}の勝ちです！`);
          }, 100);
        }
      } else {
        alert(response.message || "手の適用に失敗しました");
        handleCancel();
      }
    } catch (error) {
      console.error("手の適用エラー:", error);
      setErrorMessage("手の適用に失敗しました");
      handleCancel();
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    if (!gameId) {
      await initializeGame();
      return;
    }
    
    setIsLoading(true);
    setErrorMessage(null);
    
    const response = await apiClient.resetGame(gameId);
    
    if (response) {
      // リセット成功
      updateGameState(response.state);
      setCurrentPath([]);
      setIsAIThinking(false);
    } else {
      // リセット失敗（ゲームが存在しないなど）、新しいゲームを作成
      console.log("ゲームをリセットできませんでした。新しいゲームを作成します。");
      await initializeGame();
    }
    
    setIsLoading(false);
  };

  const handleModeChange = async (mode: GameMode) => {
    setGameMode(mode);
    await handleReset();
  };

  const handleBoardSizeChange = async (size: 9 | 18) => {
    setBoardSize(size);
    setGameId(null);
    setCurrentPath([]);
    setIsGameOver(false);
    await initializeGame(size);
  };

  return (
    <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
      {/* 左サイド - 水色プレイヤー */}
      <div className="flex-1 border-r-2 border-gray-300 flex flex-col items-center justify-center gap-8">
        {currentPlayer === 1 && !isGameOver && (
          <div className="text-2xl font-bold text-cyan-400">
            あなたの番です
          </div>
        )}
        
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">∞</span>
          </div>
          
          <div className={`flex items-center gap-3 ${playerBlocks[1].size4 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              {[...Array(4)].map((_, i) => (
                <div key={i} className={`w-5 h-5 border ${playerBlocks[1].size4 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              ))}
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残{playerBlocks[1].size4}</span>
          </div>
          
          <div className={`flex items-center gap-3 ${playerBlocks[1].size5 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              {[...Array(5)].map((_, i) => (
                <div key={i} className={`w-5 h-5 border ${playerBlocks[1].size5 > 0 ? 'bg-cyan-400 border-cyan-600' : 'bg-gray-500 border-gray-600'}`}></div>
              ))}
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残{playerBlocks[1].size5}</span>
          </div>
        </div>
      </div>
      
      {/* メイン画面（中央） */}
      <div className="flex-1 flex flex-col items-center border-r-2 border-gray-300 py-8">
        <div className="mb-4">
          <h1 className="text-4xl font-bold">
            <span className="text-cyan-400">ワタルート</span>
            <span className="text-pink-400">道場</span>
          </h1>
        </div>
        
        {/* API接続状態 */}
        {!apiConnected && (
          <div className="mb-4 px-4 py-2 bg-red-100 text-red-700 rounded">
            ⚠️ APIサーバーに接続できません
          </div>
        )}
        
        {errorMessage && (
          <div className="mb-4 px-4 py-2 bg-red-100 text-red-700 rounded">
            {errorMessage}
          </div>
        )}
        
        {/* ゲームモード選択 */}
        {/* 盤面サイズ選択 */}
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => handleBoardSizeChange(9)}
            disabled={isLoading}
            className={`px-3 py-1.5 rounded text-sm font-semibold transition ${
              boardSize === 9 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } disabled:opacity-50`}
          >
            9×9
          </button>
          <button
            onClick={() => handleBoardSizeChange(18)}
            disabled={isLoading}
            className={`px-3 py-1.5 rounded text-sm font-semibold transition ${
              boardSize === 18 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } disabled:opacity-50`}
          >
            18×18
          </button>
        </div>

        {/* ゲームモード選択 */}
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => handleModeChange('pvp')}
            disabled={isLoading}
            className={`px-4 py-2 rounded font-bold transition ${
              gameMode === 'pvp' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            } disabled:opacity-50`}
          >
            対人戦
          </button>
          <button
            onClick={() => handleModeChange('vsAPI')}
            disabled={isLoading || !apiConnected}
            className={`px-4 py-2 rounded font-bold transition ${
              gameMode === 'vsAPI' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            } disabled:opacity-50`}
          >
            vs MCTS AI
          </button>
          <button
            onClick={() => handleModeChange('vsAlphaZero')}
            disabled={isLoading || !apiConnected || boardSize !== 9}
            className={`px-4 py-2 rounded font-bold transition ${
              gameMode === 'vsAlphaZero' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            } disabled:opacity-50`}
            title={boardSize !== 9 ? "Alpha Zeroは9x9のみ対応" : ""}
          >
            🧠 vs Alpha Zero
          </button>
        </div>

        {/* AI難易度選択 */}
        {gameMode === 'vsAPI' && (
          <div className="mb-4 flex gap-2 items-center">
            <span className="text-sm font-semibold text-gray-700">AI難易度:</span>
            <button
              onClick={() => setAiDifficulty('easy')}
              disabled={isLoading || isAIThinking}
              className={`px-3 py-1.5 rounded text-sm font-semibold transition ${
                aiDifficulty === 'easy' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } disabled:opacity-50`}
            >
              簡単
              <br /> (Pure MCTS)
            </button>
            <button
              onClick={() => setAiDifficulty('hard')}
              disabled={isLoading || isAIThinking}
              className={`px-3 py-1.5 rounded text-sm font-semibold transition ${
                aiDifficulty === 'hard' 
                  ? 'bg-red-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } disabled:opacity-50`}
            >
              難しい
              <br /> (Tactical Heuristics MCTS)
            </button>
          </div>
        )}

        {isAIThinking && (
          <div className="mb-2 text-lg font-bold text-purple-600 animate-pulse">
            🤔 AIが考え中...
          </div>
        )}
        
        <div className="flex justify-center items-center mt-4 mb-6 min-h-[56px]">
          {currentPath.length > 0 ? (
            <div className="flex gap-4 mt-2">
              {currentPath.length > 2 && (
                <button
                  onClick={handleConfirm}
                  disabled={isLoading}
                  className="px-4 py-1 bg-cyan-600 text-white font-bold rounded hover:bg-cyan-700 transition disabled:opacity-50"
                >
                  確定
                </button>
              )}
              <button
                onClick={handleCancel}
                disabled={isLoading}
                className="px-4 py-1 bg-gray-500 text-white font-bold rounded hover:bg-gray-600 transition disabled:opacity-50"
              >
                キャンセル
              </button>
            </div>
          ) : (
            <div className="flex gap-4 mt-2" />
          )}
        </div>

        {/* 盤面 */}
        <div 
          className={`grid gap-0 border-t-4 border-b-4 border-l-4 border-r-4 border-t-cyan-400 border-b-cyan-400 border-l-pink-400 border-r-pink-400 ${
            boardSize === 9 ? 'grid-cols-9' : 'grid-cols-18'
          }`}
        >
          {Array.from({ length: boardSize * boardSize }).map((_, index) => {
            const row = Math.floor(index / boardSize);
            const col = index % boardSize;
            const layers = board[row]?.[col] || [0, 0];
            const layer1 = layers[0];
            const layer2 = layers[1];
            
            let bgColor = "bg-black";
            if (layer2 !== 0) {
              bgColor = layer2 === 1 ? "bg-cyan-200" : "bg-pink-200";
            } else if (layer1 !== 0) {
              bgColor = layer1 === 1 ? "bg-cyan-400" : "bg-pink-400";
            }
            
            const cellSize = boardSize === 9 ? 'w-10 h-10' : 'w-6 h-6';
            
            return (
              <div
                key={index}
                onClick={() => handleCellClick(row, col)}
                className={`${cellSize} ${bgColor} border border-gray-600 cursor-pointer hover:opacity-80 transition-all`}
              ></div>
            );
          })}
        </div>
        
        <button
          onClick={handleReset}
          disabled={isLoading}
          className="mt-6 px-6 py-2 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50"
        >
          {isLoading ? "処理中..." : "リセット"}
        </button>
      </div>
      
      {/* 右サイド - ピンクプレイヤー */}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        {currentPlayer === -1 && !isGameOver && (
          <div className="text-2xl font-bold text-pink-400">
            {(gameMode === 'vsAPI' || gameMode === 'vsAlphaZero') ? 
              (gameMode === 'vsAlphaZero' ? '🧠 Alpha Zeroの番です' : 'AIの番です') 
              : 'あなたの番です'}
          </div>
        )}
        
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">∞</span>
          </div>
          
          <div className={`flex items-center gap-3 ${playerBlocks[-1].size4 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              {[...Array(4)].map((_, i) => (
                <div key={i} className={`w-5 h-5 border ${playerBlocks[-1].size4 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              ))}
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残{playerBlocks[-1].size4}</span>
          </div>
          
          <div className={`flex items-center gap-3 ${playerBlocks[-1].size5 === 0 ? 'opacity-30' : ''}`}>
            <div className="flex gap-0.5">
              {[...Array(5)].map((_, i) => (
                <div key={i} className={`w-5 h-5 border ${playerBlocks[-1].size5 > 0 ? 'bg-pink-400 border-pink-600' : 'bg-gray-500 border-gray-600'}`}></div>
              ))}
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残{playerBlocks[-1].size5}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

