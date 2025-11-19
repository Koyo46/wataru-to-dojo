"""
GPU環境確認スクリプト

PyTorchとCUDAが正しくインストールされているか確認します。
"""

import sys

def check_gpu():
    print("=" * 60)
    print("PyTorch GPU環境チェック")
    print("=" * 60)
    
    # PyTorchのインポート
    try:
        import torch
        print(f"\n✅ PyTorchインポート成功")
        print(f"   バージョン: {torch.__version__}")
    except ImportError as e:
        print(f"\n❌ PyTorchがインストールされていません")
        print(f"   エラー: {e}")
        print("\n解決方法:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False
    
    # CUDA利用可能性チェック
    print(f"\nCUDA利用可能: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"✅ CUDAが利用可能です！")
        print(f"   CUDAバージョン: {torch.version.cuda}")
        print(f"   cuDNNバージョン: {torch.backends.cudnn.version()}")
        print(f"   GPUデバイス数: {torch.cuda.device_count()}")
        print(f"   現在のGPU: {torch.cuda.current_device()}")
        print(f"   GPU名: {torch.cuda.get_device_name(0)}")
        
        # メモリ情報
        props = torch.cuda.get_device_properties(0)
        print(f"   GPU総メモリ: {props.total_memory / 1024**3:.2f} GB")
        print(f"   マルチプロセッサ数: {props.multi_processor_count}")
        print(f"   Compute Capability: {props.major}.{props.minor}")
        
        # 簡単なテスト
        print("\n" + "=" * 60)
        print("GPU演算テスト")
        print("=" * 60)
        
        try:
            print("\n1. テンソル作成テスト...")
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            print(f"   ✅ テンソル作成成功")
            
            print("\n2. 行列演算テスト...")
            z = torch.matmul(x, y)
            print(f"   ✅ 行列演算成功")
            print(f"   結果の形状: {z.shape}")
            
            print("\n3. メモリ使用量...")
            allocated = torch.cuda.memory_allocated(0) / 1024**2
            reserved = torch.cuda.memory_reserved(0) / 1024**2
            print(f"   割り当て済みメモリ: {allocated:.2f} MB")
            print(f"   予約済みメモリ: {reserved:.2f} MB")
            
            print("\n4. ニューラルネットワークテスト...")
            import torch.nn as nn
            model = nn.Sequential(
                nn.Conv2d(4, 128, 3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
                nn.Conv2d(128, 128, 3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
            ).cuda()
            
            test_input = torch.randn(8, 4, 9, 9).cuda()  # batch=8, 9x9盤面
            output = model(test_input)
            print(f"   ✅ ニューラルネット実行成功")
            print(f"   入力形状: {test_input.shape}")
            print(f"   出力形状: {output.shape}")
            
            allocated_after = torch.cuda.memory_allocated(0) / 1024**2
            print(f"   モデル使用メモリ: {allocated_after - allocated:.2f} MB")
            
            # クリーンアップ
            del x, y, z, model, test_input, output
            torch.cuda.empty_cache()
            
            print("\n" + "=" * 60)
            print("✅ すべてのテスト成功！Alpha Zero学習の準備完了！")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ GPU演算テスト失敗")
            print(f"   エラー: {e}")
            return False
    else:
        print("\n❌ CUDAが利用できません")
        print("\n考えられる原因:")
        print("  1. PyTorchがCPU版でインストールされている")
        print("  2. CUDAドライバーの問題")
        print("  3. CUDA Toolkitのバージョン不一致")
        print("\n解決方法:")
        print("  1. 正しいPyTorchをインストール:")
        print("     pip uninstall torch torchvision torchaudio")
        print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print("\n  2. NVIDIA-SMIで確認:")
        print("     nvidia-smi")
        print("\n  3. CUDA Toolkitのインストール（必要な場合）:")
        print("     https://developer.nvidia.com/cuda-downloads")
        
        return False

if __name__ == "__main__":
    success = check_gpu()
    sys.exit(0 if success else 1)

