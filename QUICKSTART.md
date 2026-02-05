# 🚀 빠른 시작 가이드 (Quick Start)

## 5분 안에 CD 파이프라인 시작하기

### 📌 Step 1: GitHub Secrets 등록 (2분)

GitHub Repository → Settings → Secrets and variables → Actions

다음 5개 환경변수 추가:

```
DOCKER_USERNAME = jhlee8812              # Docker Hub 아이디
DOCKER_PASSWORD = dckr_pat_xxx...       # Docker Hub Access Token
WIN_HOST = 192.168.1.100                # Windows Server IP
WIN_USER = kth08                        # Windows Server 사용자명
WIN_PASS = YourPassword123!             # Windows Server 비밀번호
```

### 📌 Step 2: Windows Server 준비 (2분)

**관리자 PowerShell**에서 실행:
```powershell
Enable-PSRemoting -Force
Set-Service WinRM -StartupType Automatic
mkdir "C:\Users\kth08\Desktop\soncoding-web"
```

그리고 해당 디렉토리에 `docker-compose.yml` 복사

### 📌 Step 3: 코드 푸시 (1분)

```bash
git add .
git commit -m "Add GitHub Actions CD pipeline"
git push origin main
```

### ✅ 완료!

GitHub Actions가 자동으로 실행됩니다:
- Docker 이미지 빌드 → Docker Hub 푸시 → Windows Server 배포

---

## 📊 상태 확인

### GitHub Actions 확인
https://github.com/[USERNAME]/[REPO]/actions

### Windows Server 확인
```powershell
docker ps
docker-compose logs -f
```

---

## ⚡ 자주 사용하는 명령어

### 배포 (수동)
```batch
C:\Users\kth08\Desktop\soncoding-web\deploy.bat
```

### 상태 확인
```batch
C:\Users\kth08\Desktop\soncoding-web\test-docker-status.bat
```

### 롤백
```batch
C:\Users\kth08\Desktop\soncoding-web\rollback.bat
```

---

## 🔗 상세 문서

- **[CD_PIPELINE_GUIDE.md](CD_PIPELINE_GUIDE.md)** - 전체 설정 및 사용 가이드
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - 체크리스트 및 트러블슈팅
- **[README_DEPLOYMENT.md](README_DEPLOYMENT.md)** - 배포 구성 완료 가이드

---

## 💡 팁

**docker-compose.yml 주의사항:**
```yaml
version: '3.8'

services:
  app:
    image: thkim0812/soncoding-web:latest  # ⚠️ 이미지명 확인!
    ports:
      - "8000:8000"                        # ⚠️ 포트 충돌 확인!
```

**Secrets 복사 불가:**
- GitHub에 등록한 후 수정만 가능 (삭제 후 재등록 필요)

**첫 배포:**
- 5-10분 소요 (이미지 빌드 시간에 따라 다름)
- 이후 배포는 더 빠름 (캐싱)

---

문제가 있으면 **DEPLOYMENT_CHECKLIST.md**의 트러블슈팅 섹션을 참고하세요! 🎯
