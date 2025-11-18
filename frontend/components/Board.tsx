"use client";

import { useState } from "react";

interface BoardProps {
  // 将来的にバックエンドから盤面データを受け取る想定
  initialBoard?: number[][][];
}

export default function Board({ initialBoard }: BoardProps) {
  // board[row][col] = [layer1, layer2] (0: 空, 1: 水色, -1: ピンク)
  const [board, setBoard] = useState<number[][][]>(
    initialBoard || Array.from({ length: 18 }, () => 
      Array.from({ length: 18 }, () => [0, 0])
    )
  );

  const handleCellClick = (row: number, col: number) => {
    // 現在は描画のみ。将来的にバックエンドAPIと連携予定
    console.log(`Clicked: row=${row}, col=${col}`);
  };

  return (
    <div className="flex flex-col items-center">
      {/* タイトル */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold">
          <span className="text-cyan-400">ワタルート</span>
          <span className="text-pink-400">道場</span>
        </h1>
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

      {/* 説明テキスト */}
      <div className="mt-6 text-center text-gray-600 dark:text-gray-400">
        <p>18×18の盤面</p>
        <p className="text-sm mt-2">
          <span className="text-cyan-400">水色</span>は上下を、
          <span className="text-pink-400">ピンク</span>は左右を繋ぎます
        </p>
      </div>
    </div>
  );
}

