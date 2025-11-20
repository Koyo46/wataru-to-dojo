# Alpha Zero セットアップガイド

このガイドでは、Alpha Zeroを使ったワタルートAIの学習環境をセットアップする手順を説明します。

## 📋 前提条件

- **OS**: Windows 10/11
- **GPU**: NVIDIA GeForce GTX 1650以上
- **VRAM**: 4GB以上
- **Python**: 3.8以上
- **CUDA**: 12.x（ドライバー546.32以上）

## 🔧 セットアップ手順

### ステップ1: PyTorch + CUDA のインストール

```bash
# 仮想環境に入る
cd C:\Users\ultee\wataru-to_dojo\backend
.\venv\Scripts\activate

# PyTorch（CUDA対応版）をインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**注意**: CUDA 12.3の場合は`cu121`を使用します。

### ステップ2: 追加ライブラリのインストール

```bash
# requirements.txtに必要なライブラリが追加されているので
pip install -r requirements.txt
```

### ステップ3: GPU動作確認

```bash
cd alpha_zero
python check_gpu.py
```

**期待される出力:**

```
============================================================
PyTorch GPU環境チェック
============================================================

✅ PyTorchインポート成功
   バージョン: 2.x.x

CUDA利用可能: True
✅ CUDAが利用可能です！
   CUDAバージョン: 12.3
   GPUデバイス数: 1
   現在のGPU: 0
   GPU名: NVIDIA GeForce GTX 1650
   GPU総メモリ: 4.00 GB

============================================================
GPU演算テスト
============================================================

1. テンソル作成テスト...
   ✅ テンソル作成成功

2. 行列演算テスト...
   ✅ 行列演算成功

3. メモリ使用量...
   割り当て済みメモリ: 7.63 MB

4. ニューラルネットワークテスト...
   ✅ ニューラルネット実行成功
   入力形状: torch.Size([8, 4, 9, 9])
   出力形状: torch.Size([8, 128, 9, 9])

============================================================
✅ すべてのテスト成功！Alpha Zero学習の準備完了！
============================================================
```

### ステップ4: コンポーネントのテスト

#### 4-1. ゲームラッパーのテスト

```bash
python WataruToGame.py
```

期待される出力:
```
============================================================
WataruToGame ラッパー テスト
============================================================

盤面サイズ: (9, 9)
アクション数: 324

初期プレイヤー: 1
合法手の数: 72

最初の合法手のアクションID: 0
次のプレイヤー: -1
ゲーム終了: いいえ

✅ テスト完了！
```

#### 4-2. ニューラルネットワークのテスト

```bash
cd pytorch
python WataruToNNet.py
```

期待される出力:
```
============================================================
WataruToNNet テスト
============================================================

ネットワーク作成中...
総パラメータ数: 2,xxx,xxx
学習可能パラメータ数: 2,xxx,xxx
モデルサイズ: xx.xx MB (float32)

テスト実行中...

入力形状: torch.Size([8, 6, 9, 9])
方策出力形状: torch.Size([8, 324])
価値出力形状: torch.Size([8, 1])

方策の合計（各バッチ）: tensor([1.0000, 1.0000, ...])
価値の範囲: [-1.000, 1.000]

============================================================
CUDA テスト
============================================================
✅ CUDAで正常動作
GPU使用メモリ: xx.xx MB

✅ テスト完了！
```

#### 4-3. NNetラッパーのテスト

```bash
python NNet.py
```

期待される出力:
```
============================================================
NNetWrapper テスト
============================================================
ニューラルネットワーク作成完了
  デバイス: CUDA
  チャンネル数: 64
  残差ブロック数: 4
  総パラメータ数: xxx,xxx

予測テスト...
方策の形状: (324,)
方策の合計: 1.0000
価値: 0.xxxx

学習テスト（ダミーデータ）...

学習開始: 10例

エポック 1/2
  時間: x.xx秒
  方策損失: x.xxxx
  価値損失: x.xxxx
  合計損失: x.xxxx
  バッチ数: 1

エポック 2/2
  時間: x.xx秒
  方策損失: x.xxxx
  価値損失: x.xxxx
  合計損失: x.xxxx
  バッチ数: 1

✅ 学習完了

モデル保存/読み込みテスト...
✅ モデル保存: test_models/test.pth.tar
✅ モデル読み込み: test_models/test.pth.tar

✅ テスト完了！
```

### ステップ5: 学習開始の準備確認

すべてのテストが成功したら、学習を開始できます！

```bash
cd C:\Users\ultee\wataru-to_dojo\backend\alpha_zero
python main.py
```

## 🚨 トラブルシューティング

### ❌ CUDA が利用できない

**症状:**
```
CUDA利用可能: False
❌ CUDAが利用できません
```

**解決方法:**

1. **PyTorchのバージョン確認**
   ```bash
   python -c "import torch; print(torch.__version__)"
   ```
   
   `+cu121`が含まれていない場合、CPU版がインストールされています。
   
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. **CUDAドライバー確認**
   ```bash
   nvidia-smi
   ```
   
   エラーが出る場合は、NVIDIAドライバーを更新してください。
   https://www.nvidia.com/Download/index.aspx

3. **CUDA Toolkitの確認**
   ```bash
   nvcc --version
   ```
   
   見つからない場合でも、PyTorchには組み込まれているので通常は問題ありません。

### ❌ ModuleNotFoundError: No module named 'torch'

**解決方法:**

```bash
# 仮想環境に入っているか確認
where python
# -> C:\Users\ultee\wataru-to_dojo\backend\venv\Scripts\python.exe であることを確認

# PyTorchをインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### ❌ ImportError: cannot import name 'Coach'

**解決方法:**

alpha-zero-generalのパスが正しく設定されているか確認：

```bash
cd C:\Users\ultee\wataru-to_dojo\backend\alpha_zero
python -c "import sys; sys.path.append('../alpha-zero-general'); from Coach import Coach; print('OK')"
```

### ❌ CUDA Out of Memory

**症状:**
```
RuntimeError: CUDA out of memory. Tried to allocate xxx MiB
```

**解決方法:**

`main.py`のバッチサイズを削減：

```python
'batch_size': 32,  # 64から32に削減
```

または、ニューラルネットのサイズを削減：

```python
'num_channels': 64,      # 128から64に削減
'num_res_blocks': 4,     # 8から4に削減
```

### ❌ 学習が進まない/エラーが出る

**デバッグ方法:**

1. **プロトタイプモードで試す**
   - 小さな設定で動作確認
   - エラーを早期に発見

2. **ログを確認**
   - エラーメッセージを読む
   - スタックトレースを確認

3. **GPUメモリをクリア**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

## 📊 推奨ワークフロー

### 初めての場合

1. ✅ GPU確認（`check_gpu.py`）
2. ✅ コンポーネントテスト（各Pythonファイル）
3. ✅ プロトタイプ学習（5イテレーション、1-2時間）
4. 📊 結果確認
5. 🔧 パラメータ調整
6. 🚀 本格学習（100イテレーション、数日）

### 学習の継続

```bash
# 学習を再開（models/best.pth.tarが存在する場合）
python main.py
# -> "既存のモデルが見つかりました。続きから学習しますか？ (y/n): y"
```

## 🎯 次のステップ

セットアップが完了したら：

1. **README.md**を読んで学習フェーズを理解
2. **プロトタイプ学習**を実行（1-2時間）
3. 結果を評価
4. 本格学習に進む

---

問題が解決しない場合は、以下の情報を含めて質問してください：

- エラーメッセージ全文
- `check_gpu.py`の出力
- 実行したコマンド
- Pythonバージョン（`python --version`）
- PyTorchバージョン（`python -c "import torch; print(torch.__version__)"`）

