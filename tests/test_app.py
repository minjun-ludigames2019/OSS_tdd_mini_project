import pytest
from app import app, game_state

@pytest.fixture
def client():
    # 테스트 실행 전 상태 초기화 (독립적인 테스트 환경 구성)
    game_state["gold"] = 1000
    game_state["stage"] = 1
    game_state["eq_level"] = 0
    game_state["eq_rarity"] = 0
    game_state["eq_base_atk"] = 10
    game_state["enemy_hp"] = 100
    game_state["max_enemy_hp"] = 100
    game_state["inventory"] = [0, 0, 0, 0, 0] # 일반 장비 5개
    
    with app.test_client() as client:
        yield client

def test_home(client):
    # 메인 페이지(HTML)가 잘 렌더링되는지 테스트
    response = client.get('/')
    assert response.status_code == 200
    assert b'MVP' in response.data  # HTML 안에 'MVP'라는 단어가 포함되었는지 확인

def test_status(client):
    # 서버 상태 조회 API 테스트
    response = client.get('/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data["state"]["gold"] == 1000

def test_combat_tick(client):
    # 전투 로직 테스트
    response = client.get('/combat_tick')
    assert response.status_code == 200
    data = response.get_json()
    assert data["state"]["enemy_hp"] < 100 

def test_enhance_success(client):
    # 강화 로직 테스트
    response = client.get('/enhance')
    assert response.status_code == 200
    data = response.get_json()
    assert "Success" in data["msg"]
    assert game_state["gold"] == 950 # 1000 - 50 (비용 차감 확인)

def test_synthesize(client):
    # 합성 로직 테스트
    response = client.get('/synthesize')
    assert response.status_code == 200
    data = response.get_json()
    assert 1 in game_state["inventory"] # 일반(0) 5개가 합성되어 고급(1)이 생겼는지 확인