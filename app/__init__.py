from flask import Flask
from flasgger import Swagger  # Flasgger 불러오기

# Flask 앱 객체 생성
app = Flask(__name__)
swagger = Swagger(app)        # Flask 앱에 Swagger 적용

# 라우트(경로) 파일 임포트
# 주의: 순환 참조(Circular Import) 오류를 막기 위해 반드시 파일 맨 아래에 적어주세요!
from app import routes