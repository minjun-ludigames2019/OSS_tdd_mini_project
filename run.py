# app 패키지(__init__.py)에서 생성된 app 객체를 가져옵니다.
from app import app

if __name__ == '__main__':
    # 디버그 모드로 서버 실행 (운영 환경에서는 False로 변경)
    app.run(debug=True)