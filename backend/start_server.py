"""
APIサーバー起動スクリプト

開発用のサーバーを起動します。
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("ワタルート道場 - バックエンドAPI サーバー")
    print("=" * 60)
    print()
    print("サーバーを起動しています...")
    print()
    print("アクセス先:")
    print("  - API: http://localhost:8000")
    print("  - ドキュメント: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print()
    print("サーバーを停止するには Ctrl+C を押してください")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

