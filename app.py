from flask import Flask, jsonify, render_template

app = Flask(__name__)

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

# 1. 메인 화면 접속 시 HTML 파일을 렌더링해서 보여줍니다.
@app.route('/')
def home():
    return render_template('index.html')

# 2. 현재 서버의 게임 상태만 가져오는 API
@app.route('/status')
def get_status():
    return jsonify({"state": game_state})

@app.route('/combat_tick')
def combat_tick():
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

@app.route('/enhance')
def enhance():
    cost = 50 + (game_state["eq_level"] * 25)
    if game_state["gold"] < cost:
        return jsonify({"error": "Not enough gold", "state": game_state})
    
    game_state["gold"] -= cost
    game_state["eq_level"] += 1
    return jsonify({"msg": f"Enhance Success! (+{game_state['eq_level']})", "state": game_state})

@app.route('/synthesize')
def synthesize():
    cost = 100 
    if game_state["gold"] < cost:
        return jsonify({"error": "Not enough gold (Need 100G)", "state": game_state})
    
    normal_count = game_state["inventory"].count(0)
    if normal_count >= 5:
        game_state["gold"] -= cost
        sets = normal_count // 5
        game_state["inventory"] = [x for x in game_state["inventory"] if x != 0]
        for _ in range(sets):
            game_state["inventory"].append(1)
        return jsonify({"msg": f"Synthesized {sets} items!", "state": game_state})
    
    return jsonify({"error": "Not enough items.", "state": game_state})

if __name__ == '__main__':
    app.run(debug=True)