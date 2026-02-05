# 📚 CD 파이프라인 구성 완료 가이드

## 🎯 생성된 파일 목록

### 1️⃣ GitHub Actions Workflow
**파일**: `.github/workflows/deploy.yml`
- GitHub에 코드 푸시 시 자동으로 Docker 이미지 빌드
- Docker Hub에 이미지 푸시
- Windows Server에 PowerShell Remoting으로 배포

### 2️⃣ 배포 스크립트
**파일**: `deploy.bat`
- Windows Server에서 실행
- 자동으로 컨테이너 정지 → 이미지 제거 → 최신 이미지 다운로드 → 새 컨테이너 시작
- 배포 진행 상황 상세 로깅

### 3️⃣ 보조 스크립트
- **`test-docker-status.bat`**: Docker 상태 빠른 확인
- **`rollback.bat`**: 배포 실패 시 이전 버전으로 롤백

### 4️⃣ 설정 문서
- **`CD_PIPELINE_GUIDE.md`**: 전체 파이프라인 설정 및 사용 가이드
- **`DEPLOYMENT_CHECKLIST.md`**: 체크리스트 및 트러블슈팅 가이드

---

## 🔐 필수 GitHub Secrets 설정

GitHub Repository의 **Settings → Secrets and variables → Actions**에서 다음 5개 환경 변수를 추가하세요:

| 환경변수명 | 값 | 설명 |
|-----------|-----|------|
| `DOCKER_USERNAME` | 예: `jhlee8812` | Docker Hub 아이디 |
| `DOCKER_PASSWORD` | 예: `dckr_pat_...` | Docker Hub Access Token |
| `WIN_HOST` | 예: `192.168.1.100` | Windows Server IP 주소 |
| `WIN_USER` | 예: `kth08` 또는 `DOMAIN\kth08` | Windows Server 사용자명 |
| `WIN_PASS` | Windows Server 로그인 비밀번호 | Windows Server 비밀번호 |

### 🔑 Docker Hub Access Token 생성
1. [docker.com](https://docker.com) 접속 및 로그인
2. 계정 메뉴 → **Account Settings**
3. **Security** → **New Access Token**
4. 이름 입력 (예: `github-actions`)
5. **Read & Write** 권한 선택
6. **Generate** 클릭 후 Token 복사

---

## 🪟 Windows Server 필수 설정

### 1. PowerShell Remoting 활성화

Windows Server에서 **관리자 권한** PowerShell 실행:

```powershell
# PowerShell Remoting 활성화
Enable-PSRemoting -Force

# WinRM 서비스 시작
Start-Service WinRM

# 자동 시작 설정
Set-Service WinRM -StartupType Automatic

# 방화벽 규칙 추가 (필요시)
netsh advfirewall firewall add rule name="Allow WinRM" dir=in action=allow protocol=tcp localport=5985
```

### 2. 배포 디렉토리 준비

Windows Server의 해당 경로에 배포 디렉토리 생성:

```powershell
# 예: C:\Users\kth08\Desktop\soncoding-web\
mkdir C:\Users\[USERNAME]\Desktop\soncoding-web

# 다음 파일들을 이 디렉토리에 복사:
# - docker-compose.yml
# - dockerfile (필요시)
```

### 3. Docker 설치 확인

```powershell
docker --version
docker-compose --version
```

---

## 🚀 배포 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                    1. 개발자 코드 푸시                       │
│                    git push origin main                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              2. GitHub Actions 자동 실행                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Build & Push Job (ubuntu-latest)                     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ ✓ Checkout code                                      │  │
│  │ ✓ Docker Hub 로그인                                  │  │
│  │ ✓ Docker 이미지 빌드                                 │  │
│  │ ✓ Docker Hub에 이미지 푸시                           │  │
│  │   (이미지명: thkim0812/soncoding-web:latest)         │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│                   ▼                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Deploy Job (windows-latest)                          │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ ✓ Windows Server PowerShell 원격 접속                │  │
│  │ ✓ deploy.bat 스크립트 실행                           │  │
│  │   (원격 실행)                                         │  │
│  └────────────────┬─────────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               3. Windows Server 배포                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ deploy.bat 실행 (자동)                               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ 1️⃣ 기존 컨테이너 중지                                │  │
│  │    docker-compose down -f                            │  │
│  │                                                       │  │
│  │ 2️⃣ 기존 이미지 제거                                  │  │
│  │    docker rmi thkim0812/soncoding-web:latest -f     │  │
│  │                                                       │  │
│  │ 3️⃣ 최신 이미지 다운로드                              │  │
│  │    docker pull thkim0812/soncoding-web:latest       │  │
│  │                                                       │  │
│  │ 4️⃣ 새 컨테이너 시작                                  │  │
│  │    docker-compose up -d                              │  │
│  │                                                       │  │
│  │ 5️⃣ 배포 결과 확인                                    │  │
│  │    docker ps / docker logs                           │  │
│  └────────────────┬─────────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
              ✅ 배포 완료
        (FastAPI 서버 실행 중)
```

---

## 📋 실행 순서

### 초기 설정 (일회성)
1. ✅ GitHub Secrets 5개 등록
2. ✅ Windows Server PowerShell Remoting 활성화
3. ✅ Windows Server에 배포 디렉토리 생성
4. ✅ docker-compose.yml 배포 디렉토리에 복사
5. ✅ Repository에 모든 파일 커밋 & 푸시

### 매 배포마다
1. 📝 코드 수정 후 커밋
2. 🔄 `git push origin main` 실행
3. 👀 GitHub Actions 로그 확인
4. ✅ 배포 완료 확인

---

## ✨ 주요 특징

### ✅ 자동화
- 코드 푸시만으로 CI/CD 자동 실행
- 수동 배포 작업 불필요

### ✅ 로깅
- GitHub Actions에서 전체 과정 기록
- Windows Server 배포 로그 상세 기록
- 컨테이너 로그 자동 표시

### ✅ 안정성
- 기존 컨테이너 자동 정지
- 이전 이미지 자동 제거
- 배포 실패 시 로그로 원인 파악 가능

### ✅ 유연성
- 필요시 수동 배포 가능 (`deploy.bat` 실행)
- 롤백 스크립트 제공
- 상태 확인 스크립트 제공

---

## 🔍 배포 상태 확인

### GitHub Actions에서 확인
```
Repository → Actions → 최신 워크플로우 선택 → 로그 확인
```

### Windows Server에서 확인
```powershell
# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인 (중지된 것도 포함)
docker ps -a

# 컨테이너 로그 확인
docker-compose logs -f

# 실시간 리소스 사용량 확인
docker stats
```

---

## 📞 트러블슈팅 빠른 참조

| 문제 | 원인 | 해결 방법 |
|------|------|---------|
| Build 실패 | Docker Hub 인증 오류 | Secrets 재확인, Token 재생성 |
| Deploy 실패 | Windows Server 미응답 | `Enable-PSRemoting`, 방화벽 확인 |
| 컨테이너 미실행 | 포트 충돌 | `netstat` 명령어로 포트 확인 |
| 이전 버전 실행 | 캐시 문제 | `docker rmi -f` 강제 제거 |

상세 트러블슈팅은 **DEPLOYMENT_CHECKLIST.md** 참고

---

## 📚 전체 문서 구조

```
프로젝트 루트/
├── .github/
│   └── workflows/
│       └── deploy.yml                    # GitHub Actions 워크플로우
├── deploy.bat                            # 배포 스크립트 (Windows Server 실행)
├── test-docker-status.bat                # 상태 확인 스크립트
├── rollback.bat                          # 롤백 스크립트
├── CD_PIPELINE_GUIDE.md                  # 📖 전체 설정 가이드
├── DEPLOYMENT_CHECKLIST.md               # ✅ 체크리스트 & 트러블슈팅
├── README_DEPLOYMENT.md                  # 📚 이 문서
└── [기존 파일들...]
```

---

## 🎓 학습 자료

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Docker Hub 가이드](https://docs.docker.com/docker-hub/)
- [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands)
- [Docker Compose](https://docs.docker.com/compose/)

---

## ✍️ 참고사항

### 1. 이미지 이름 변경
기본값: `thkim0812/soncoding-web:latest`

다른 이름을 사용하려면:
1. `deploy.yml`의 `tags:` 항목 수정
2. `deploy.bat`의 `IMAGE_NAME` 변수 수정
3. `docker-compose.yml`의 `image:` 항목 수정

### 2. 포트 변경
기본값: `8000:8000` (FastAPI) + `3306:3306` (MySQL)

변경하려면:
1. `docker-compose.yml`의 `ports:` 수정
2. Windows Server의 방화벽 규칙 업데이트

### 3. 환경 변수
`docker-compose.yml`에서 필요한 환경 변수 설정:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` 등

---

준비 완료! 🎉 이제 배포할 준비가 되었습니다.
