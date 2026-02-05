# GitHub Actions CD 파이프라인 구성 가이드

## 📋 개요

이 파이프라인은 다음과 같은 흐름으로 동작합니다:
1. **CI**: 코드 변경 시 GitHub Actions에서 Docker 이미지 빌드
2. **Push**: 빌드된 이미지를 Docker Hub에 푸시
3. **CD**: Windows Server에 SSH 접속 후 배포 스크립트 실행

```
GitHub Push
    ↓
GitHub Actions CI (Build & Push to Docker Hub)
    ↓
Windows Server 배포 (Pull & Run Containers)
    ↓
배포 완료
```

---

## 🔐 GitHub Secrets 설정

GitHub Repository Settings에서 다음 환경 변수를 설정하세요:

### 1. Docker Hub 인증 정보
- **`DOCKER_USERNAME`**: Docker Hub 아이디
- **`DOCKER_PASSWORD`**: Docker Hub Access Token

**Docker Hub Access Token 생성 방법:**
1. docker.com에 로그인
2. Account Settings → Security → New Access Token
3. Read & Write 권한 선택
4. Token 값 복사

### 2. Windows Server 접속 정보
- **`WIN_HOST`**: Windows Server IP 주소 (예: 192.168.0.100)
- **`WIN_USER`**: Windows Server 사용자명 (도메인 형식: DOMAIN\USERNAME)
- **`WIN_PASS`**: Windows Server 비밀번호

---

## 🐳 Docker Hub 준비

1. **Docker Hub에서 Repository 생성**
   - 이름: `soncoding-web`
   - 접근성: Public 또는 Private

2. **로컬에서 이미지 빌드 및 푸시 테스트**
   ```bash
   docker build -t thkim0812/soncoding-web:latest .
   docker login
   docker push thkim0812/soncoding-web:latest
   ```

---

## 🪟 Windows Server 준비

### 필수 사항
- Windows Server 2019 이상
- Docker Desktop 설치 (Windows Server 2019에서는 Docker Server)
- PowerShell Remoting 활성화
- 방화벽 설정 (SSH/RDP 포트 개방)

### PowerShell Remoting 활성화 (관리자 권한)

```powershell
# Enable-PSRemoting 명령어 실행
Enable-PSRemoting -Force

# WinRM 서비스 시작
Start-Service WinRM

# 자동 시작 설정
Set-Service WinRM -StartupType Automatic

# 원격 접속 테스트
Test-NetConnection -ComputerName [Windows_Server_IP] -Port 5985
```

### docker-compose.yml 준비

Windows Server의 배포 디렉토리에 다음 파일들이 있어야 합니다:
- `docker-compose.yml`
- `dockerfile` (필요시)

**권장 경로**: `C:\Users\[USERNAME]\Desktop\soncoding-web\`

---

## 📝 GitHub Actions Workflow 상세

### deploy.yml 구조

**1. Build and Push Job**
- Docker 이미지 빌드
- Docker Hub에 푸시
- 캐싱 활용으로 빌드 시간 단축

**2. Deploy to Windows Job**
- Windows Server에 PowerShell Remoting으로 접속
- deploy.bat 실행
- 배포 결과 로깅

---

## 🚀 배포 프로세스

### 자동 배포
```
git push → GitHub Actions 트리거 → 이미지 빌드 및 푸시 → Windows Server 배포
```

### 수동 배포 (Windows Server)
```powershell
# 배포 스크립트 실행
C:\Users\[USERNAME]\Desktop\soncoding-web\deploy.bat
```

---

## 🛠 deploy.bat 상세 기능

| 단계 | 작업 | 설명 |
|------|------|------|
| 1 | Directory Check | 배포 디렉토리 확인 및 이동 |
| 2 | Docker Version | Docker 설치 확인 |
| 3 | Stop Containers | docker-compose down으로 기존 컨테이너 중지 |
| 4 | Remove Old Image | 기존 이미지 강제 제거 |
| 5 | Pull Latest Image | Docker Hub에서 최신 이미지 다운로드 |
| 6 | Start Containers | docker-compose up으로 새 컨테이너 시작 |
| 7 | Verify | 배포 결과 확인 |
| 8 | Logs | 컨테이너 로그 표시 |

---

## ✅ 확인 사항

### 파이프라인이 정상 작동하는지 확인

1. **GitHub Actions 로그 확인**
   - Repository → Actions → 최근 워크플로우 선택
   - 각 Job의 성공/실패 확인

2. **Docker Hub에 이미지 푸시 확인**
   - docker.com → 해당 Repository → Tags 확인

3. **Windows Server 배포 확인**
   ```powershell
   # 원격 세션에서 실행
   docker ps
   docker logs soncoding-app
   ```

---

## ⚠️ 트러블슈팅

### 1. GitHub Actions 실패: "Docker login failed"
- `DOCKER_USERNAME`, `DOCKER_PASSWORD` 확인
- Docker Hub Access Token이 유효한지 확인

### 2. Windows Server 접속 실패
- `WIN_HOST`, `WIN_USER`, `WIN_PASS` 확인
- Windows Server에서 `Enable-PSRemoting` 실행
- 방화벽에서 포트 5985 개방 확인

### 3. 이미지 풀 실패
- Docker Hub에서 이미지 가용성 확인
- Docker Hub 권한 설정 확인 (Private repository인 경우)

### 4. 컨테이너 시작 실패
- Windows Server의 docker-compose.yml 경로 확인
- 포트 충돌 확인: `docker ps`로 기존 컨테이너 확인
- Docker 네트워크 설정 확인: `docker network ls`

---

## 🔄 배포 흐름 다이어그램

```
┌─────────────────┐
│   Git Push      │ (main/master 브랜치)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ GitHub Actions CI Job       │
├─────────────────────────────┤
│ 1. Checkout Code           │
│ 2. Login to Docker Hub      │
│ 3. Build Docker Image       │
│ 4. Push to Docker Hub       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ GitHub Actions Deploy Job   │
├─────────────────────────────┤
│ 1. Connect to Win Server    │
│ 2. Run deploy.bat           │
│ 3. Log Results              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Windows Server              │
├─────────────────────────────┤
│ 1. Stop Old Containers      │
│ 2. Remove Old Image         │
│ 3. Pull Latest Image        │
│ 4. Start New Containers     │
│ 5. Verify Deployment        │
└─────────────────────────────┘
         │
         ▼
    ✅ 배포 완료
```

---

## 📚 추가 리소스

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🎯 다음 단계

1. ✅ GitHub Secrets 설정
2. ✅ Windows Server 준비
3. ✅ docker-compose.yml 배포 경로에 복사
4. ✅ Repository에 코드 푸시
5. ✅ GitHub Actions 로그 확인
6. ✅ 배포 결과 확인
