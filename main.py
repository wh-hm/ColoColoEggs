from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="ColoColoEggs API")

# フロントエンドからのアクセスを許可（CORS設定）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ペットのデータ構造
class PetState(BaseModel):
    stage: int = 0  # 0: たまご, 1: こども, 2: おとな
    hunger: int = 50
    energy: int = 50
    affection: int = 50
    turns: int = 0
    isAlive: bool = True
    message: str = "たまごを温めて育てよう！"

# 時間経過と判定処理（共通ロジック）
def process_turn(pet: PetState, manual: bool = False) -> PetState:
    if not pet.isAlive:
        return pet

    pet.turns += 1
    pet.hunger = max(0, pet.hunger - 10)

    # 進化ロジック
    if pet.stage == 0 and pet.turns >= 2:
        pet.stage = 1
        pet.message = "たまごから赤ちゃんが生まれました！"
    elif pet.stage == 1 and pet.turns >= 8:
        pet.stage = 2
        pet.message = "ペットが大人の姿に進化しました！"
    elif manual:
        pet.message = "時間を過ごしました。"

    # 死亡判定
    if pet.hunger <= 0:
        pet.energy = max(0, pet.energy - 20)

    if pet.energy <= 0:
        pet.isAlive = False
        pet.message = "力尽きてしまいました…"

    return pet

# --- エンドポイント（API） ---

@app.get("/")
def read_root():
    return {"message": "コロコロたまご API 稼働中！"}

# 初期状態の取得
@app.get("/api/pet/init", response_model=PetState)
def init_pet():
    return PetState()

# ごはんをあげる
@app.post("/api/pet/feed", response_model=PetState)
def feed_pet(pet: PetState):
    if not pet.isAlive:
        return pet
    pet.hunger = min(100, pet.hunger + 30)
    pet.energy = min(100, pet.energy + 5)
    pet.message = "ごはんを食べてお腹がいっぱい！"
    return process_turn(pet, manual=False)

# あそぶ
@app.post("/api/pet/play", response_model=PetState)
def play_pet(pet: PetState):
    if not pet.isAlive:
        return pet
    if pet.energy < 20:
        pet.message = "疲れていて遊べそうにありません…"
        return pet
    
    pet.affection = min(100, pet.affection + 15)
    pet.hunger = max(0, pet.hunger - 15)
    pet.energy = max(0, pet.energy - 20)
    pet.message = "元気に遊んで満足そうです！"
    return process_turn(pet, manual=False)

# ねかせる
@app.post("/api/pet/sleep", response_model=PetState)
def sleep_pet(pet: PetState):
    if not pet.isAlive:
        return pet
    pet.energy = min(100, pet.energy + 40)
    pet.hunger = max(0, pet.hunger - 10)
    pet.message = "ぐっすり眠って体力が回復しました！"
    return process_turn(pet, manual=False)

# なにもしない（時間経過）
@app.post("/api/pet/pass_time", response_model=PetState)
def pass_time_api(pet: PetState):
    if not pet.isAlive:
        return pet
    return process_turn(pet, manual=True)