# 🔧 CD 파이프라인 통합 세팅 가이드

## 📋 작업 순서

### Phase 1: 코드 개선 (로컬)
### Phase 2: GitHub 설정
### Phase 3: Windows Server 준비
### Phase 4: 배포 테스트

---

## Phase 1️⃣ : 코드 개선 (로컬)

### Step 1-1: .gitignore 파일 생성
**목적**: .env 파일이 Git에 커밋되지 않도록 방지

**파일 위치**: 프로젝트 루트 (이미 생성됨)

**확인:**
```bash
ls -la .gitignore
cat .gitignore  # .env 포함 확인
```

### Step 1-2: .env.example 파일 생성
**목적**: 환경 변수 템플릿 제공 (개발자용)

**파일 위치**: 프로젝트 루트 (이미 생성됨)

**사용법:**
```bash
# 로컬 개발용 .env 파일 생성
cp .env.example .env

# 실제 값으로 수정
cat .env
# DB_PASSWORD=your_secure_password 로 변경
```

### Step 1-3: docker-compose.yml 개선 (선택사항)
**목적**: 환경 변수 기반 설정, 헬스 체크, 네트워크 등 추가

**비교:**
| 항목 | 현재 | 개선 |
|------|------|------|
| 환경변수 | 하드코딩 | `${DB_PASSWORD}` |
| 헬스 체크 | 없음 | 추가됨 |
| 초기 SQL | 수동 | 자동 로드 |
| 네트워크 | 기본 | 명시적 정의 |

**적용 방법:**
```bash
# 백업
cp docker-compose.yml docker-compose.yml.backup

# 새 파일로 교체
cp docker-compose.yml.improved docker-compose.yml
```

### Step 1-4: dockerfile 개선 (선택사항)
**목적**: 멀티 스테이지 빌드, 보안 강화

**개선 사항:**
- ✅ 이미지 크기 감소
- ✅ root 권한 제거
- ✅ 헬스 체크 추가
- ✅ 메타데이터 추가

**적용 방법:**
```bash
# 백업
cp dockerfile dockerfile.backup

# 새 파일로 교체
cp dockerfile.improved dockerfile
```

---

## Phase 2️⃣ : GitHub 설정

### Step 2-1: 변경사항 커밋
```bash
# 현재 상태 확인
git status

# 모든 변경사항 스테이징
git add .

# .env 파일이 포함되지 않았는지 확인
git status  # .env가 목록에 없어야 함

# 커밋
git commit -m "Add CD pipeline and security improvements

- Add .gitignore for .env files
- Add .env.example template
- Add GitHub Actions workflow (deploy.yml)
- Add Windows Server deployment scripts
- Improve docker-compose.yml with env variables
- Improve dockerfile with multi-stage build and security
- Add comprehensive documentation"
```

### Step 2-2: GitHub에 푸시
```bash
git push origin main
# 또는
git push origin master
```

### Step 2-3: GitHub Secrets 등록

**경로**: Repository → Settings → Secrets and variables → Actions

**등록할 5개 변수:**

#### 🐳 Docker Hub 정보
```
DOCKER_USERNAME = [Docker Hub 아이디]
DOCKER_PASSWORD = [Docker Hub Access Token]
```

**Docker Hub Access Token 생성:**
1. docker.com 로그인
2. Account Settings → Security
3. New Access Token → 이름 입력 (github-actions)
4. Read & Write 선택
5. Generate → Token 복사 → GitHub에 등록

#### 🪟 Windows Server 정보
```
WIN_HOST = [Windows Server IP 주소]
WIN_USER = [Windows Server 사용자명]
WIN_PASS = [Windows Server 비밀번호]
```

**Windows Server 정보 확인:**
```powershell
# IP 주소 확인
ipconfig
# IPv4 Address 값 복사

# 사용자명 확인
whoami
# DOMAIN\USERNAME 또는 USERNAME 형식

# 비밀번호는 현재 설정된 로그인 비밀번호
```

---

## Phase 3️⃣ : Windows Server 준비

### Step 3-1: PowerShell Remoting 활성화

**Windows Server에서 관리자 권한 PowerShell 실행:**

```powershell
# PowerShell Remoting 활성화
Enable-PSRemoting -Force

# WinRM 서비스 상태 확인
Get-Service WinRM

# WinRM 서비스 시작
Start-Service WinRM

# 자동 시작 설정
Set-Service WinRM -StartupType Automatic

# 방화벽 규칙 추가
netsh advfirewall firewall add rule name="Allow WinRM HTTP" dir=in action=allow protocol=tcp localport=5985

# 확인
Test-NetConnection -ComputerName localhost -Port 5985 -InformationLevel Detailed
```

### Step 3-2: 배포 디렉토리 생성

```powershell
# 디렉토리 생성
mkdir "C:\Users\[USERNAME]\Desktop\soncoding-web"

# 확인
Get-ChildItem "C:\Users\[USERNAME]\Desktop\"
```

**[USERNAME] 확인:**
```powershell
$env:USERNAME
# 출력값이 [USERNAME]
```

### Step 3-3: 파일 복사

배포 디렉토리에 **다음 파일들** 복사:

```
C:\Users\[USERNAME]\Desktop\soncoding-web\
├── docker-compose.yml      ✅ 복사 필수
├── dockerfile              ✅ 복사 필수
├── .env                    ✅ 복사 필수 (환경 변수 포함)
└── .env.example            (참고용)
```

**복사 방법:**

```bash
# 로컬에서 Windows Server로 복사 (로컬 PowerShell)
$source = "C:\Users\[LOCAL_USERNAME]\OneDrive\Desktop\Server\Server_test\s\"
$dest = "\\[WIN_HOST]\c$\Users\[WIN_USER]\Desktop\soncoding-web\"

Copy-Item -Path "$source\docker-compose.yml" -Destination $dest -Force
Copy-Item -Path "$source\dockerfile" -Destination $dest -Force
Copy-Item -Path "$source\.env" -Destination $dest -Force
```

### Step 3-4: .env 파일 설정 (Windows Server)

Windows Server의 `.env` 파일 수정:

```bash
# 원격 접속
$session = New-PSSession -ComputerName [WIN_HOST] -Credential $credential

# 파일 수정 (원격)
Invoke-Command -Session $session -ScriptBlock {
    $envPath = "C:\Users\[WIN_USER]\Desktop\soncoding-web\.env"
    
    # 현재 내용 확인
    Get-Content $envPath
    
    # 비밀번호 설정
    # DB_PASSWORD=secure_password로 변경
}
```

### Step 3-5: Docker 설치 확인

```powershell
# Docker 버전 확인
docker --version

# Docker Compose 버전 확인
docker-compose --version

# Docker 실행 상태 확인
Get-Service Docker
```

**Docker가 없으면:**
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) 설치
- 또는 Windows Server 2019에서는 [Docker Server](https://docs.microsoft.com/en-us/virtualization/windowscontainers/quick-start/set-up-environment) 설치

---

## Phase 4️⃣ : 배포 테스트

### Step 4-1: 로컬 테스트 (GitHub Actions 전)

```bash
# 1. 환경 변수 확인
cat .env

# 2. Docker Compose 검증
docker-compose config

# 3. 로컬에서 실행 (테스트)
docker-compose up -d

# 4. 컨테이너 확인
docker ps

# 5. 헬스 체크
curl http://localhost:8000

# 6. 데이터베이스 확인
docker-compose logs db

# 7. API 로그 확인
docker-compose logs app

# 8. 정지
docker-compose down
```

### Step 4-2: GitHub Actions 실행

```bash
# 1. 코드 푸시 (GitHub Actions 트리거)
git add .
git commit -m "Test CD pipeline"
git push origin main

# 2. GitHub Actions 모니터링
# Repository → Actions → 최신 workflow 클릭
```

**각 Job 확인:**
- ✅ **Build and Push Job**
  - ✓ Checkout code
  - ✓ Login to Docker Hub
  - ✓ Build Docker image
  - ✓ Push to Docker Hub
  
- ✅ **Deploy Job**
  - ✓ Connect to Windows Server
  - ✓ Run deploy.bat
  - ✓ Verify deployment

### Step 4-3: Windows Server 배포 확인

```powershell
# 1. 컨테이너 확인
docker ps

# 2. 예상 출력:
# CONTAINER ID   IMAGE                              STATUS
# [id]          thkim0812/soncoding-web:latest    Up 2 minutes

# 3. 로그 확인
docker-compose logs -f

# 4. API 테스트
curl http://localhost:8000
# 또는
Invoke-WebRequest -Uri "http://localhost:8000" -Method Get | Select-Object Content

# 5. 데이터베이스 테스트
docker exec soncoding-db mysql -uroot -p$DB_PASSWORD -Dsuhodang -e "SELECT * FROM users LIMIT 1;"
```

### Step 4-4: 배포 결과 확인

| 항목 | 확인 방법 | 성공 기준 |
|------|---------|---------|
| Docker Hub | docker.com → 아이디 → Repositories | `soncoding-web:latest` 있음 |
| GitHub Actions | Repository → Actions | ✅ 모든 Job 성공 |
| Windows Server | PowerShell → docker ps | `soncoding-app` 컨테이너 실행중 |
| FastAPI | curl http://localhost:8000 | 200 OK + JSON 응답 |
| MySQL | docker exec ... mysql | 데이터베이스 접근 가능 |

---

## 🔍 배포 후 모니터링

### 실시간 로그 확인
```powershell
docker-compose logs -f
```

### 성능 모니터링
```powershell
docker stats
```

### 컨테이너 상태
```powershell
docker ps -a
docker inspect soncoding-app
```

---

## ⚠️ 문제 해결

### 문제 1: GitHub Actions 빌드 실패
```
❌ Build and Push Job 실패
```

**해결:**
1. GitHub Secrets 확인: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
2. Docker Hub Access Token 유효성 확인
3. 로컬에서 `docker login` 테스트

### 문제 2: Windows Server 배포 실패
```
❌ Deploy Job 실패
```

**해결:**
1. Windows Server IP 확인: `ipconfig` (WIN_HOST)
2. PowerShell Remoting 활성화 확인
3. WinRM 서비스 실행 상태 확인
4. 방화벽 포트 5985 개방 확인

### 문제 3: 컨테이너 미실행
```
❌ docker ps에 soncoding-app 없음
```

**해결:**
1. 배포 디렉토리 확인: `C:\Users\[USERNAME]\Desktop\soncoding-web\`
2. docker-compose.yml 위치 확인
3. .env 파일 확인
4. 로그 확인: `docker-compose logs`

### 문제 4: MySQL 연결 실패
```
❌ FastAPI에서 DB 연결 불가
```

**해결:**
1. .env의 DB_PASSWORD 확인
2. docker-compose.yml의 환경변수 확인
3. MySQL 헬스 체크 확인: `docker ps` (healthy 상태)
4. 로그 확인: `docker-compose logs db`

---

## ✅ 최종 체크리스트

### 코드 준비 ✓
- [ ] .gitignore 생성됨
- [ ] .env.example 생성됨
- [ ] docker-compose.yml 개선됨 (선택사항)
- [ ] dockerfile 개선됨 (선택사항)
- [ ] GitHub Actions workflow 생성됨
- [ ] 배포 스크립트 생성됨

### GitHub 설정 ✓
- [ ] 코드 커밋 완료
- [ ] 코드 푸시 완료
- [ ] Secrets 5개 등록 완료
  - [ ] DOCKER_USERNAME
  - [ ] DOCKER_PASSWORD
  - [ ] WIN_HOST
  - [ ] WIN_USER
  - [ ] WIN_PASS

### Windows Server 준비 ✓
- [ ] PowerShell Remoting 활성화
- [ ] WinRM 서비스 시작
- [ ] 배포 디렉토리 생성
- [ ] 필수 파일 복사
  - [ ] docker-compose.yml
  - [ ] dockerfile
  - [ ] .env
- [ ] Docker 설치 확인
- [ ] docker-compose 설치 확인

### 배포 테스트 ✓
- [ ] 로컬 테스트 성공
- [ ] GitHub Actions 실행 성공
- [ ] Docker Hub에 이미지 생성됨
- [ ] Windows Server에 컨테이너 실행됨
- [ ] FastAPI 서버 응답 확인
- [ ] MySQL 연결 확인

---

## 🎉 완료!

모든 설정이 완료되었습니다! 이제 자동화된 CD 파이프라인이 준비되었습니다.

**자동 배포 흐름:**
```
Code Push → GitHub Actions → Docker Hub → Windows Server
```

**모니터링:**
- GitHub Actions: https://github.com/[USERNAME]/[REPO]/actions
- Docker Hub: https://docker.com → Repositories
- Windows Server: `docker ps` / `docker logs`
