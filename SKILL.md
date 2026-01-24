## skill.md
- 資料はタイムスタンプ付き（西暦年月日）で日本語で作成する
- 同じコマンドは自動的に許可すること
- ファイル命名規則: `yyyymmdd-hhmm_日本語タイトル.md`
  - 例: `20260122-1430_学習用PC要件.md`

## 利用環境

### WSL2 学習環境
| 項目 | 値 |
|------|-----|
| ディストリビューション | Ubuntu-22.04 |
| ユーザー名 | kenji |
| Miniconda | `/home/kenji/miniconda3/` |
| Conda環境名 | `donkey` |
| Python | 3.11 |
| Donkey Car | 5.2.0 |
| TensorFlow | 2.15.1 (GPU対応) |
| GPU | GTX 1660 Ti |
| プロジェクトパス | `/home/kenji/mycar/` |

### WSL2コマンド実行方法
- WSL2での作業は `wsl -d Ubuntu-22.04 -- bash -c "..."` で直接実行する
- aptなど時間のかかるコマンドも直接実行すること
- conda環境を使う場合は以下のように有効化する：
  ```bash
  wsl -d Ubuntu-22.04 -- bash -c "source /home/kenji/miniconda3/etc/profile.d/conda.sh && conda activate donkey && <コマンド>"
  ```

### パス対応表
| Windows | WSL2 |
|---------|------|
| `C:\Users\thefu\Documents\donkeycar\` | `/mnt/c/Users/thefu/Documents/donkeycar/` |
| WSL2ホーム | `/home/kenji/` |
| Windowsからアクセス | `\\wsl$\Ubuntu-22.04\home\kenji\` |
