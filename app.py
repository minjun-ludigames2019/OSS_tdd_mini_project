from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # AI가 테스트 코드에서 기대한 문구를 그대로 반환합니다.
    return "Welcome to TDD Service"

if __name__ == '__main__':
    app.run(debug=True)