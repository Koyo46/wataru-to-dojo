"""
デプロイ前のチェックスクリプト

デプロイ前に必要なファイルと設定が揃っているか確認します。
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """ファイルの存在をチェック"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}が見つかりません: {filepath}")
        return False

def check_requirements():
    """requirements.txtの内容をチェック"""
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"❌ {req_file}が見つかりません")
        return False
    
    with open(req_file, 'r') as f:
        content = f.read()
        
    # uvicorn[standard]が含まれていないことを確認
    if "uvicorn[standard]" in content:
        print("❌ requirements.txtに 'uvicorn[standard]' が含まれています")
        print("   'uvicorn' に変更してください（Renderでのビルドエラーを回避）")
        return False
    
    # 必要なパッケージが含まれているか確認
    required_packages = ["fastapi", "uvicorn", "pydantic"]
    missing = []
    for pkg in required_packages:
        if pkg not in content:
            missing.append(pkg)
    
    if missing:
        print(f"❌ 必要なパッケージが見つかりません: {', '.join(missing)}")
        return False
    
    print(f"✅ {req_file}の内容は正常です")
    return True

def check_imports():
    """Pythonのインポートをチェック"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from game.game import WataruToGame
        from game.move import Move, Position
        from game.board import Board
        print("✅ Pythonモジュールのインポートは正常です")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def main():
    print("=" * 60)
    print("デプロイ前チェック")
    print("=" * 60)
    print()
    
    checks = []
    
    # ファイルの存在チェック
    print("📁 ファイルの存在チェック:")
    checks.append(check_file_exists("requirements.txt", "requirements.txt"))
    checks.append(check_file_exists("api/main.py", "FastAPI メインファイル"))
    checks.append(check_file_exists("game/game.py", "ゲームロジック"))
    checks.append(check_file_exists("game/move.py", "手の管理"))
    checks.append(check_file_exists("game/board.py", "盤面管理"))
    print()
    
    # requirements.txtの内容チェック
    print("📦 requirements.txtの内容チェック:")
    checks.append(check_requirements())
    print()
    
    # インポートチェック
    print("🐍 Pythonモジュールのインポートチェック:")
    checks.append(check_imports())
    print()
    
    # 結果
    print("=" * 60)
    if all(checks):
        print("✅ すべてのチェックが成功しました！")
        print("   Renderにデプロイする準備ができています。")
        print()
        print("次のステップ:")
        print("1. GitHubにコードをプッシュ")
        print("2. Renderでリポジトリを接続")
        print("3. render.yamlを使用してデプロイ")
        return 0
    else:
        print("❌ いくつかのチェックが失敗しました。")
        print("   上記のエラーを修正してから再度実行してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

