from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flasgger import Swagger

app = Flask(__name__)
# 세션(로그인 상태) 유지를 위한 시크릿 키 설정
app.secret_key = "rpg_super_secret_key" 
# Flasgger 초기화
swagger = Swagger(app)

# 임시 사용자 데이터베이스 (아이디: 비밀번호)
users_db = {}

# 게임 상태 (기존 구조 유지)
game_state = {
    "gold": 100,
    "stage": 1,
    "inventory": [],  
    "eq_level": 0,
    "eq_rarity": 0,
    "eq_base_atk": 10,
    "enemy_hp": 100,
    "max_enemy_hp": 100
}

# ==========================================
#  화면 렌더링 라우트 (HTML 제공)
# ==========================================

@app.route('/login')
def login_page():
    """로그인 및 회원가입 페이지를 렌더링합니다."""
    # 이미 로그인된 상태라면 메인 게임 화면으로 이동
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/')
def home():
    """메인 게임 화면을 렌더링합니다."""
    # 로그인하지 않은 사용자는 로그인 페이지로 튕겨냅니다.
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')


# ==========================================
#  API 라우트 (Flasgger OpenAPI 문서화 적용)
# ==========================================

@app.route('/api/register', methods=['POST'])
def register():
    """신규 사용자 회원가입
    아이디와 비밀번호를 받아 새로운 계정을 생성합니다.
    ---
    tags:
      - Auth API
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: 회원가입 성공
      400:
        description: 이미 존재하는 아이디
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users_db:
        return jsonify({"error": "Already existing username"}), 400
    
    users_db[username] = password
    return jsonify({"msg": f"User {username} registered successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """사용자 로그인
    아이디와 비밀번호를 확인하고 세션을 생성합니다.
    ---
    tags:
      - Auth API
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: 로그인 성공
      401:
        description: 비밀번호 불일치 또는 존재하지 않는 아이디
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if users_db.get(username) == password:
        session['username'] = username  # 세션에 로그인 정보 저장
        return jsonify({"msg": "Login successful"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """사용자 로그아웃
    현재 로그인된 세션을 파기합니다.
    ---
    tags:
      - Auth API
    responses:
      200:
        description: 로그아웃 성공
    """
    session.pop('username', None)
    return jsonify({"msg": "Logout successful"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """현재 게임 상태 조회
    로그인한 유저의 현재 게임 진행 상태(골드, 스테이지 등)를 불러옵니다.
    ---
    tags:
      - Game API
    responses:
      200:
        description: 게임 상태 정보 반환
    """
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"state": game_state})

@app.route('/api/combat', methods=['POST'])
def combat_tick():
    """전투 수행 (1 틱)
    적을 공격하고 HP가 0이 되면 보상을 획득합니다.
    ---
    tags:
      - Game API
    responses:
      200:
        description: 전투 결과 및 갱신된 게임 상태 반환
    """
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    rarity_multipliers = {0: 1, 1: 2, 2: 5, 3: 15, 4: 50}
    multiplier = rarity_multipliers.get(game_state["eq_rarity"], 1)
        
    combat_power = int(game_state["eq_base_atk"] * multiplier * (1 + game_state["eq_level"] * 0.2))
    game_state["enemy_hp"] -= combat_power
    log_msg = f"Dealt {combat_power} damage."

    if game_state["enemy_hp"] <= 0:
        earned_gold = 10 + int(game_state["stage"] * 2)
        game_state["gold"] += earned_gold
        log_msg += f" Enemy killed! +{earned_gold}G"
        game_state["stage"] += 1
        game_state["max_enemy_hp"] += 150
        game_state["enemy_hp"] = game_state["max_enemy_hp"]
        
        game_state["inventory"].append(0)
        log_msg += " Item dropped!"

    return jsonify({"msg": log_msg, "state": game_state, "cp": combat_power})

@app.route('/api/enhance', methods=['POST'])
def enhance():
    """장비 강화
    골드를 소모하여 장비 레벨을 올립니다.
    ---
    tags:
      - Game API
    responses:
      200:
        description: 강화 성공 여부 및 결과
      400:
        description: 골드 부족
    """
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cost = 50 + (game_state["eq_level"] * 25)
    if game_state["gold"] < cost:
        return jsonify({"error": "Not enough gold", "state": game_state}), 400
    
    game_state["gold"] -= cost
    game_state["eq_level"] += 1
    return jsonify({"msg": f"Enhance Success! (+{game_state['eq_level']})", "state": game_state})

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    """아이템 합성
    100G를 소모하여 인벤토리의 0등급 아이템 5개를 1등급 아이템 1개로 합성합니다.
    ---
    tags:
      - Game API
    responses:
      200:
        description: 합성 성공
      400:
        description: 골드 부족 또는 아이템 부족
    """
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cost = 100 
    if game_state["gold"] < cost:
        return jsonify({"error": "Not enough gold (Need 100G)", "state": game_state}), 400
    
    normal_count = game_state["inventory"].count(0)
    if normal_count >= 5:
        game_state["gold"] -= cost
        sets = normal_count // 5
        game_state["inventory"] = [x for x in game_state["inventory"] if x != 0]
        for _ in range(sets):
            game_state["inventory"].append(1)
        return jsonify({"msg": f"Synthesized {sets} items!", "state": game_state}), 200
    
    return jsonify({"error": "Not enough items.", "state": game_state}), 400


if __name__ == '__main__':
    app.run(debug=True)