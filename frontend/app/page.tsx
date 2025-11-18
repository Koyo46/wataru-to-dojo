"use client";

import Board from "../components/Board";

export default function Home() {
  return (
    <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
      {/* 左サイド - 水色プレイヤー情報 */}
      <div className="flex-1 border-r-2 border-gray-300 flex flex-col items-center justify-center gap-8">
        <div className="text-2xl font-bold text-cyan-400">
          水色プレイヤー
        </div>
        
        {/* ブロック表示 */}
        <div className="flex flex-col gap-4">
          {/* 3マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">∞</span>
          </div>
          
          {/* 4マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残1</span>
          </div>
          
          {/* 5マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
              <div className="w-5 h-5 bg-cyan-400 border border-cyan-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残1</span>
          </div>
        </div>
      </div>
      
      {/* メイン画面（中央） - 盤面 */}
      <div className="flex-1 flex flex-col items-center border-r-2 border-gray-300 py-8">
        <Board />
      </div>
      
      {/* 右サイド - ピンクプレイヤー情報 */}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        <div className="text-2xl font-bold text-pink-400">
          ピンクプレイヤー
        </div>
        
        {/* ブロック表示 */}
        <div className="flex flex-col gap-4">
          {/* 3マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">∞</span>
          </div>
          
          {/* 4マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残1</span>
          </div>
          
          {/* 5マスブロック */}
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
              <div className="w-5 h-5 bg-pink-400 border border-pink-600"></div>
            </div>
            <span className="text-lg font-bold text-black dark:text-white">残1</span>
          </div>
        </div>
      </div>
    </div>
  );
}

