# MainkurafutoAI (Integrated Bedrock Agent) [Beta]

**[日本語 / Japanese]**
## 概要
MainkurafutoAIは、Minecraft統合版（Bedrock Edition）のための自律型AIエージェントです。
「最強のAI」を目指し、5層のアーキテクチャ（反射、技能、計画、マッピング、対話）を組み合わせて動作します。

### 技術スタック
- **言語**: Python 3.10+
- **視覚**: MSS (スクリーンショット), OpenCV (画像処理), Tesseract (OCR)
- **入力**: ViGEmBus / vgamepad (仮想Xboxコントローラー)
- **計画**: LLM (Mock/Stub実装)

### セットアップ
1. Python 3.10以上をインストール。
2. 依存ライブラリをインストール:
   ```bash
   pip install -r requirements.txt
   ```
3. (オプション) 座標認識のためにTesseract OCRをインストールしてください。
4. (Windows) 仮想コントローラーを使用するために `ViGEmBus` ドライバーが必要です。

### 使用方法
1. Minecraft統合版を起動。
2. エージェントを実行:
   ```bash
   python main.py
   ```
3. ゲーム画面をフォーカスしてください。
4. **操作**:
   - `F12`: 一時停止 / 再開
   - `End`: 終了 (Kill Switch)
   - コンソール: `goal: <タスク>` で計画機能をテストできます。

---

**[English]**
## Overview
MainkurafutoAI is an autonomous AI agent for Minecraft Bedrock Edition.
Designed to be the "Strongest Integrated AI", it utilizes a 5-layer architecture: Reflex, Skill, Planning, Mapping, and Interface.

### Tech Stack
- **Language**: Python 3.10+
- **Vision**: MSS (Screen Capture), OpenCV (Processing), Tesseract (OCR)
- **Input**: ViGEmBus / vgamepad (Virtual Xbox Controller)
- **Planning**: LLM (Mock/Stub implementation)

### Setup
1. Install Python 3.10 or higher.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install Tesseract OCR for coordinate reading.
4. (Windows) Install `ViGEmBus` drivers to enable the virtual controller.

### Usage
1. Open Minecraft Bedrock Edition.
2. Run the agent:
   ```bash
   python main.py
   ```
3. Focus the Minecraft window.
4. **Controls**:
   - `F12`: Pause / Resume
   - `End`: Kill Switch (Stop Agent)
   - Console: Type `goal: <Task>` to test the planning feature.

---

## License
This project is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)**.
本プロジェクトは **クリエイティブ・コモンズ 表示 - 非営利 - 改変禁止 4.0 国際 (CC BY-NC-ND 4.0)** の下にライセンスされています。
