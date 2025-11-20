"""
Alpha Zeroモデルのダウンロードとロード管理

本番環境で自動的にモデルをダウンロードする機能を提供
"""

import os
import urllib.request
from pathlib import Path
from typing import Optional


class ModelLoader:
    """モデルファイルを複数のソースから読み込む"""
    
    # デフォルトのGitHubリリースURL
    DEFAULT_MODEL_URL = "https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar"
    
    @staticmethod
    def load_model_path(model_path: Optional[str] = None) -> str:
        """
        モデルパスを取得（存在しない場合はダウンロード）
        
        優先順位:
        1. 引数で指定されたパス
        2. 環境変数 ALPHAZERO_MODEL_PATH で指定されたローカルパス
        3. デフォルトのローカルパス (開発環境用)
        4. 環境変数 ALPHAZERO_MODEL_URL からダウンロード
        5. デフォルトURLからダウンロード
        
        Args:
            model_path: モデルファイルのパス（オプション）
            
        Returns:
            利用可能なモデルファイルのパス
            
        Raises:
            FileNotFoundError: モデルが見つからずダウンロードもできない場合
        """
        # 1. 引数で指定されたパスを確認
        if model_path and os.path.exists(model_path):
            print(f"[OK] モデル発見（引数指定）: {model_path}")
            return model_path
        
        # 2. 環境変数で指定されたパスを確認
        env_path = os.getenv('ALPHAZERO_MODEL_PATH')
        if env_path and os.path.exists(env_path):
            print(f"[OK] モデル発見（環境変数）: {env_path}")
            return env_path
        
        # 3. デフォルトのローカルパスを確認（開発環境用）
        local_paths = [
            'alpha_zero/models/best.pth.tar',
            'backend/alpha_zero/models/best.pth.tar',
            os.path.join(os.path.dirname(__file__), 'models', 'best.pth.tar'),
        ]
        
        for path in local_paths:
            if os.path.exists(path):
                print(f"[OK] モデル発見（ローカル）: {path}")
                return path
        
        # 4. リモートからダウンロード
        print("[INFO] ローカルにモデルが見つかりません")
        print("[INFO] リモートからモデルをダウンロードします...")
        
        # ダウンロード先パス（本番環境では /tmp を使用）
        download_path = os.getenv('ALPHAZERO_MODEL_PATH', '/tmp/alphazero/best.pth.tar')
        
        # ダウンロード元URL
        remote_url = os.getenv('ALPHAZERO_MODEL_URL', ModelLoader.DEFAULT_MODEL_URL)
        
        try:
            return ModelLoader._download(remote_url, download_path)
        except Exception as e:
            raise FileNotFoundError(
                f"モデルファイルが見つからず、ダウンロードも失敗しました: {e}\n"
                f"以下のいずれかを設定してください:\n"
                f"1. ALPHAZERO_MODEL_PATH環境変数（ローカルパス）\n"
                f"2. ALPHAZERO_MODEL_URL環境変数（ダウンロードURL）\n"
                f"デフォルトURL: {ModelLoader.DEFAULT_MODEL_URL}"
            )
    
    @staticmethod
    def _download(url: str, local_path: str) -> str:
        """
        URLからファイルをダウンロード
        
        Args:
            url: ダウンロード元URL
            local_path: 保存先パス
            
        Returns:
            ダウンロードしたファイルのパス
            
        Raises:
            Exception: ダウンロード失敗時
        """
        # 既にファイルがある場合はスキップ
        if os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            if file_size > 1000000:  # 1MB以上なら有効なファイルとみなす
                print(f"[OK] モデルは既に存在: {local_path} ({file_size / 1024 / 1024:.1f} MB)")
                return local_path
        
        # ディレクトリを作成
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"[INFO] モデルをダウンロード中...")
        print(f"   URL: {url}")
        print(f"   保存先: {local_path}")
        
        try:
            # プログレスバー付きダウンロード
            def report(count, block_size, total_size):
                if total_size > 0:
                    percent = min(int(count * block_size * 100 / total_size), 100)
                    downloaded = count * block_size / 1024 / 1024
                    total = total_size / 1024 / 1024
                    print(f"\r   進捗: {percent}% ({downloaded:.1f}/{total:.1f} MB)", end='')
            
            urllib.request.urlretrieve(url, local_path, reporthook=report)
            print(f"\n[OK] ダウンロード完了: {local_path}")
            
            # ファイルサイズを確認
            file_size = os.path.getsize(local_path)
            print(f"   ファイルサイズ: {file_size / 1024 / 1024:.1f} MB")
            
            if file_size < 100000:  # 100KB未満は異常
                raise Exception(f"ダウンロードしたファイルが小さすぎます ({file_size} bytes)")
            
            return local_path
            
        except Exception as e:
            # ダウンロード失敗時、不完全なファイルを削除
            if os.path.exists(local_path):
                os.remove(local_path)
            print(f"\n[ERROR] ダウンロード失敗: {e}")
            raise


def test_model_loader():
    """モデルローダーのテスト"""
    print("=" * 60)
    print("Model Loader Test")
    print("=" * 60)
    
    try:
        model_path = ModelLoader.load_model_path()
        print(f"\n[OK] Success: model_path = {model_path}")
        
        # ファイルの存在確認
        if os.path.exists(model_path):
            size = os.path.getsize(model_path)
            print(f"   File size: {size / 1024 / 1024:.2f} MB")
        else:
            print(f"[WARNING] Path returned but file does not exist")
            
    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_model_loader()

