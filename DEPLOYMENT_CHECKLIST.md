# CD 파이프라인 설정 체크리스트

## 📋 사전 준비 사항

### GitHub Repository 설정
- [ ] Repository 접근 가능
- [ ] main 또는 master 브랜치 존재
- [ ] `.github/workflows/deploy.yml` 파일 생성됨

### GitHub Secrets 설정
Repository → Settings → Secrets and variables → Actions에서:
- [ ] `DOCKER_USERNAME` 설정 (Docker Hub 아이디)
- [ ] `DOCKER_PASSWORD` 설정 (Docker Hub Access Token)
- [ ] `WIN_HOST` 설정 (Windows Server IP 주소)
- [ ] `WIN_USER` 설정 (Windows Server 사용자명)
- [ ] `WIN_PASS` 설정 (Windows Server 비밀번호)

### Docker Hub 준비
- [ ] Docker Hub 계정 생성/확인
- [ ] Repository 생성: `soncoding-web`
- [ ] Access Token 생성 및 복사
- [ ] 로컬에서 이미지 테스트 푸시 완료

### Windows Server 준비
- [ ] Windows Server 2019 이상 설치
- [ ] Docker Desktop 또는 Docker Server 설치
- [ ] PowerShell Remoting 활성화됨
- [ ] WinRM 서비스 시작됨
- [ ] 방화벽 포트 5985 개방
- [ ] 배포 디렉토리 생성: `C:\Users\[USERNAME]\Desktop\soncoding-web\`
- [ ] `docker-compose.yml` 파일 복사
- [ ] `dockerfile` 파일 복사

---

## 🚀 첫 배포 실행 단계

### Step 1: 모든 파일이 준비되었는지 확인
```
프로젝트 루트/
├── .github/
│   └── workflows/
│       └── deploy.yml          ✓ 자동 생성됨
├── dockerfile                   ✓ 기존 파일
├── docker-compose.yml          ✓ 기존 파일
├── main.py                     ✓ 기존 파일
├── requirements.txt            ✓ 기존 파일
├── deploy.bat                  ✓ 자동 생성됨
├── test-docker-status.bat      ✓ 자동 생성됨
├── rollback.bat                ✓ 자동 생성됨
└── CD_PIPELINE_GUIDE.md        ✓ 자동 생성됨
```

### Step 2: GitHub에 코드 푸시
```bash
git add .
git commit -m "Add CD pipeline with GitHub Actions"
git push origin main
```

### Step 3: GitHub Actions 실행 모니터링
1. GitHub Repository 접속
2. Actions 탭 클릭
3. 실행 중인 워크플로우 확인
4. 각 Job의 로그 확인

### Step 4: Windows Server 배포 확인
Windows Server에서:
```powershell
# 배포 결과 확인
docker ps
docker ps -a
docker logs soncoding-app

# 컨테이너 상태 확인
docker-compose ps
```

---

## 🔧 트러블슈팅 가이드

### 문제 1: "Build and Push" Job 실패

**원인**: Docker Hub 인증 실패

**해결 방법**:
1. GitHub Secrets에서 `DOCKER_USERNAME`, `DOCKER_PASSWORD` 확인
2. Docker Hub에서 Access Token 다시 생성
3. Token에 읽기/쓰기 권한이 있는지 확인

```bash
# 로컬에서 테스트
docker login -u [DOCKER_USERNAME] -p [DOCKER_PASSWORD]
docker build -t [DOCKER_USERNAME]/soncoding-web:latest .
docker push [DOCKER_USERNAME]/soncoding-web:latest
```

### 문제 2: "Deploy to Windows" Job 실패

**원인**: Windows Server 접속 실패

**해결 방법**:

#### A. 네트워크 연결 확인
```bash
ping [WIN_HOST]  # Windows Server IP가 응답하는지 확인
```

#### B. PowerShell Remoting 설정 확인
Windows Server에서 관리자 권한으로 PowerShell 실행:
```powershell
# 상태 확인
Get-Service WinRM

# 활성화 (비활성화된 경우)
Enable-PSRemoting -Force
Start-Service WinRM
Set-Service WinRM -StartupType Automatic

# 테스트
Test-NetConnection -ComputerName [WIN_HOST] -Port 5985 -InformationLevel Detailed
```

#### C. 방화벽 확인
```powershell
# WinRM 예외 추가
netsh advfirewall firewall add rule name="Allow WinRM HTTP" dir=in action=allow protocol=tcp localport=5985

# 또는 Windows Defender Firewall에서 수동 추가
# Settings → Privacy & Security → Windows Defender Firewall → Allow an app through firewall
# → Windows Remote Management (HTTP-In) 체크
```

#### D. 자격증명 확인
- `WIN_USER`: 사용자명 (도메인 포함 시 DOMAIN\USERNAME 형식)
- `WIN_PASS`: 현재 비밀번호 (변경되었다면 Secrets 업데이트)

#### E. 경로 확인
Windows Server에서:
```powershell
# 배포 경로 확인
Test-Path "C:\Users\$env:USERNAME\Desktop\soncoding-web"

# docker-compose.yml 확인
Get-Content "C:\Users\$env:USERNAME\Desktop\soncoding-web\docker-compose.yml"
```

### 문제 3: 컨테이너가 시작되지 않음

**원인**: 포트 충돌, 네트워크 문제, 이미지 문제

**해결 방법**:

#### A. 포트 충돌 확인
```powershell
# 포트 사용 확인
netstat -ano | findstr ":8000"  # FastAPI 포트
netstat -ano | findstr ":3306"  # MySQL 포트
```

#### B. 이미지 확인
```powershell
# Docker 로그 확인
docker-compose logs -f

# 이미지 상태 확인
docker images
docker pull thkim0812/soncoding-web:latest
```

#### C. 네트워크 확인
```powershell
# Docker 네트워크 확인
docker network ls
docker network inspect bridge

# 컨테이너 네트워크 재설정
docker-compose down
docker network prune
docker-compose up -d
```

### 문제 4: 배포 후에도 이전 버전이 실행됨

**원인**: 이미지 캐시 문제, 컨테이너 미재시작

**해결 방법**:
```powershell
# 강제 재배포
deploy.bat  # 기존 배포 스크립트는 자동으로 정리함

# 또는 수동으로
docker-compose down --remove-orphans
docker rmi thkim0812/soncoding-web:latest -f
docker pull thkim0812/soncoding-web:latest
docker-compose up -d
```

---

## 📊 배포 상태 모니터링

### GitHub Actions에서 모니터링
1. Repository → Actions 탭
2. 최신 워크플로우 클릭
3. 각 Job 상태 확인

### Windows Server에서 모니터링
```powershell
# 실시간 로그 확인
docker-compose logs -f

# 컨테이너 상태 확인
docker ps

# 성능 모니터링
docker stats

# 이미지 히스토리 확인
docker history thkim0812/soncoding-web:latest
```

---

## 🔄 롤백 방법

### 배포 실패 시 이전 버전으로 복구

**옵션 1: 자동 롤백** (배포 실패 시)
- GitHub Actions에서 배포 실패
- Windows Server의 기존 이미지 유지

**옵션 2: 수동 롤백**
```powershell
# 1. 현재 컨테이너 중지
docker-compose down

# 2. 이전 이미지 확인
docker images thkim0812/soncoding-web

# 3. 특정 태그로 컨테이너 시작 (docker-compose.yml에서 태그 변경)
# 예: thkim0812/soncoding-web:v1.0.0

# 4. 다시 시작
docker-compose up -d
```

**옵션 3: 스크립트 사용**
```powershell
C:\path\to\rollback.bat
```

---

## 📞 지원 및 추가 정보

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Docker 공식 문서](https://docs.docker.com/)
- [PowerShell Remoting 가이드](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands)

---

마지막 업데이트: 2024년
