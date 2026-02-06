# 📊 프로젝트 코드 분석 및 CD 파이프라인 통합 가이드

## 🎯 현재 프로젝트 구조 분석

### 프로젝트 개요
- **이름**: Soncoding Web API
- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **데이터베이스**: MySQL 8.0
- **배포**: Docker + Docker Compose

---

## 📁 프로젝트 구조

```
soncoding-web/
├── main.py                           # FastAPI 메인 서버
├── requirements.txt                  # 파이썬 의존성
├── dockerfile                        # Docker 이미지 정의
├── docker-compose.yml                # 멀티 컨테이너 설정
├── .env                              # 환경 변수 (로컬 테스트용)
│
├── database/
│   ├── init_db.py                    # DB 초기화
│   ├── dependencies.py               # DB 연결 의존성
│   ├── schema.sql                    # 테이블 스키마
│   └── data.sql                      # 초기 데이터
│
├── routers/
│   ├── __init__.py
│   ├── contents.py                   # 콘텐츠 관련 API
│   ├── submissions.py                # 제출 관련 API
│   ├── community.py                  # 커뮤니티 관련 API
│   └── announcements.py              # 공지사항 관련 API
│
├── schemas/
│   ├── __init__.py
│   ├── content_schema.py             # 콘텐츠 스키마
│   ├── submission_schema.py          # 제출 스키마
│   ├── post_schema.py                # 포스트 스키마
│   ├── comment_schema.py             # 댓글 스키마
│   ├── announcement_schema.py        # 공지사항 스키마
│   └── user_schema.py                # 사용자 스키마
│
├── services/
│   └── ocr_service.py                # OCR 서비스
│
├── tests/
│   ├── test_contents_router.py
│   ├── test_submissions_router.py
│   ├── test_db_dependencies.py
│   ├── test_ocr_service.py
│   └── test_schemas.py
│
├── .github/
│   └── workflows/
│       └── deploy.yml                # GitHub Actions CD 파이프라인 ✨
│
└── [문서들]
    ├── CD_PIPELINE_GUIDE.md
    ├── DEPLOYMENT_CHECKLIST.md
    ├── README_DEPLOYMENT.md
    └── QUICKSTART.md
```

---

## 🔍 주요 파일 분석

### 1️⃣ main.py - FastAPI 메인 서버
```python
✅ FastAPI 앱 초기화
✅ 라이프사이클 관리 (startup/shutdown)
✅ DB 초기화 (startup 시)
✅ 4개 라우터 포함:
   - /api/contents (콘텐츠)
   - /api/submissions (제출)
   - /api/community (커뮤니티)
   - /api/announcements (공지사항)
✅ 기본 엔드포인트: GET /
```

**포트**: 8000

---

### 2️⃣ dockerfile - Docker 이미지
```dockerfile
✅ 기본 이미지: python:3.11-slim
✅ 작업 디렉토리: /app
✅ 의존성 설치: pip install -r requirements.txt
✅ 소스코드 복사: COPY . .
✅ 노출 포트: 8000
✅ 시작 명령어: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### 3️⃣ docker-compose.yml - 멀티 컨테이너
```yaml
서비스 1: MySQL (soncoding-db)
  - 포트: 3306:3306
  - 볼륨: db_data (데이터 영속성)
  - 환경변수:
    - MYSQL_DATABASE: suhodang
    - MYSQL_ROOT_PASSWORD: 1234 ⚠️ 주의!

서비스 2: FastAPI (soncoding-app)
  - 포트: 8000:8000
  - 의존성: MySQL
  - 환경변수:
    - DB_HOST: db
    - DB_USER: root
    - DB_PASSWORD: your_password ⚠️ 주의!
    - DB_NAME: suhodang
```

---

### 4️⃣ database/dependencies.py - DB 연결
```python
✅ MySQL 커넥터 사용
✅ 환경 변수 기반 설정:
   - DB_HOST
   - DB_USER
   - DB_PASSWORD
   - DB_NAME
✅ FastAPI 의존성 주입 패턴
✅ 자동 연결 해제
```

---

### 5️⃣ database/init_db.py - DB 초기화
```python
✅ schema.sql 실행 (테이블 생성)
✅ data.sql 실행 (초기 데이터)
✅ 서버 시작 시 자동 실행 (main.py의 lifespan)
```

---

## ⚠️ 현재 문제점 및 수정 필요 사항

### 🔴 Critical (즉시 수정)

#### 1. docker-compose.yml 환경 변수 하드코딩
**현재:**
```yaml
MYSQL_ROOT_PASSWORD: 1234
DB_PASSWORD: your_password
```

**문제**: 비밀번호가 코드에 노출됨

**해결안**: 환경 변수로 변경
```yaml
MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
DB_PASSWORD: ${DB_PASSWORD}
```

#### 2. .env 파일이 안전하지 않음
**현재**: 실제 비밀번호가 로컬 .env에 저장

**문제**: Git에 커밋되면 안됨

**해결안**:
```bash
# .gitignore에 추가
.env
```

#### 3. dockerfile 보안
**현재**: root 권한으로 실행

**권장**: 일반 사용자로 실행
```dockerfile
RUN useradd -m appuser
USER appuser
```

---

### 🟡 Important (CD 파이프라인용 수정)

#### 4. docker-compose.yml 포트 설정
**Windows Server 배포 시 고려사항:**
- 포트 8000: FastAPI 앱
- 포트 3306: MySQL

**확인사항:**
- [ ] Windows Server에서 포트 8000 사용 가능?
- [ ] 포트 충돌 없음?
- [ ] 방화벽 설정?

#### 5. volumes 설정
**현재:**
```yaml
volumes:
  db_data:  # Named volume
```

**Windows Server에서는:**
```yaml
# 옵션 1: Named volume (권장)
volumes:
  db_data:

# 옵션 2: Bind mount
volumes:
  - C:\docker-data\soncoding-db:/var/lib/mysql
```

---

### 🟢 Enhancement (선택사항)

#### 6. 헬스 체크 추가
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### 7. 로깅 설정
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### 8. 리소스 제한
```yaml
resources:
  limits:
    cpus: '1'
    memory: 512M
  reservations:
    cpus: '0.5'
    memory: 256M
```

---

## 📋 CD 파이프라인에 필요한 변수들

### GitHub Secrets (5개) ✅ 이미 설정함
```
DOCKER_USERNAME     = Docker Hub 아이디
DOCKER_PASSWORD     = Docker Hub Token
WIN_HOST           = Windows Server IP
WIN_USER           = Windows Server 사용자명
WIN_PASS           = Windows Server 비밀번호
```

### 추가로 필요한 변수들

#### A. 환경 변수 파일 (.env)
Windows Server에서 사용:
```
DB_HOST=db
DB_USER=root
DB_PASSWORD=[보안된 비밀번호]
DB_NAME=suhodang
```

#### B. docker-compose.yml에서 사용
```yaml
MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
DB_PASSWORD=${DB_PASSWORD}
```

---

## 🔧 수정이 필요한 파일들

### 파일 1: docker-compose.yml
```diff
services:
  db:
    image: mysql:8.0
    container_name: soncoding-db
    restart: always
    environment:
      MYSQL_DATABASE: suhodang
-     MYSQL_ROOT_PASSWORD: 1234
+     MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-1234}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

  app:
    build: .
    container_name: soncoding-app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: root
-     DB_PASSWORD: your_password
+     DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: suhodang
```

### 파일 2: dockerfile (선택사항)
```diff
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

+# 보안: 일반 사용자로 실행
+RUN useradd -m appuser
+USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 파일 3: .gitignore
```diff
# 환경 변수
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml
```

---

## 🚀 CD 파이프라인 실행 흐름

### Step 1: 로컬 개발
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env)
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=1234
DB_NAME=suhodang
EOF

# 3. 로컬 테스트
python main.py
# 또는
uvicorn main:app --reload
```

### Step 2: Docker 로컬 테스트 (Windows Server와 동일)
```bash
# 1. 이미지 빌드
docker build -t soncoding-web:latest .

# 2. 컨테이너 실행 (docker-compose)
docker-compose up -d

# 3. 테스트
curl http://localhost:8000

# 4. 로그 확인
docker-compose logs -f

# 5. 정지
docker-compose down
```

### Step 3: GitHub에 푸시
```bash
git add .
git commit -m "Update docker-compose with env variables"
git push origin main
```

### Step 4: GitHub Actions 자동 실행
1. **Build & Push Job**
   - 이미지 빌드: `thkim0812/soncoding-web:latest`
   - Docker Hub에 푸시

2. **Deploy Job**
   - Windows Server 원격 접속
   - deploy.bat 실행:
     - 기존 컨테이너 정지
     - 기존 이미지 제거
     - 새 이미지 다운로드
     - 새 컨테이너 시작

### Step 5: 배포 확인 (Windows Server)
```powershell
# 1. 컨테이너 확인
docker ps

# 2. 로그 확인
docker-compose logs -f

# 3. 서버 접속 테스트
curl http://localhost:8000
# 또는
Invoke-WebRequest -Uri "http://localhost:8000" -Method Get
```

---

## 📊 데이터 흐름

```
클라이언트 요청
    ↓
FastAPI (포트 8000)
    ↓
MySQL (포트 3306)
    ↓
데이터베이스 응답
    ↓
JSON 응답
    ↓
클라이언트
```

---

## 🧪 테스트 체크리스트

### 로컬 환경 테스트
- [ ] `pip install -r requirements.txt` 성공
- [ ] `uvicorn main:app --reload` 실행 성공
- [ ] `curl http://localhost:8000` 응답 OK

### Docker 테스트
- [ ] `docker build -t soncoding-web:latest .` 성공
- [ ] `docker-compose up -d` 성공
- [ ] MySQL 컨테이너 실행 확인
- [ ] FastAPI 컨테이너 실행 확인
- [ ] `curl http://localhost:8000` 응답 OK
- [ ] DB 데이터 확인
- [ ] `docker-compose down` 성공

### GitHub Actions 테스트
- [ ] 코드 푸시 후 Actions 실행 확인
- [ ] Build & Push Job 성공
- [ ] Docker Hub에 이미지 존재 확인
- [ ] Deploy Job 성공
- [ ] Windows Server에 배포 확인

### Windows Server 테스트
- [ ] `docker ps` 컨테이너 실행 확인
- [ ] `docker logs soncoding-app` 에러 없음
- [ ] 외부에서 `http://[WIN_HOST]:8000` 접근 가능
- [ ] MySQL 데이터 접근 가능

---

## 📝 최종 체크리스트

### 코드 수정
- [ ] docker-compose.yml에서 환경 변수화
- [ ] .gitignore 생성 및 .env 등록
- [ ] dockerfile 보안 개선 (선택사항)

### GitHub 설정
- [ ] GitHub Secrets 5개 등록
- [ ] .gitignore 파일 커밋

### Windows Server 설정
- [ ] PowerShell Remoting 활성화
- [ ] 배포 디렉토리 생성
- [ ] docker-compose.yml 복사
- [ ] .env 파일 생성 (보안)

### 배포 테스트
- [ ] 코드 푸시 → GitHub Actions 실행
- [ ] Docker Hub에 이미지 생성 확인
- [ ] Windows Server 배포 확인
- [ ] 서버 동작 확인

---

## 🎯 다음 단계

1. **docker-compose.yml 수정** (환경 변수화)
2. **.gitignore 생성** (.env 등록)
3. **GitHub에 푸시** (모든 변경사항)
4. **GitHub Secrets 등록** (5개 변수)
5. **첫 배포 테스트** (코드 푸시 → 자동 배포)
6. **Windows Server 확인** (컨테이너 실행 확인)

준비 완료! 🚀
