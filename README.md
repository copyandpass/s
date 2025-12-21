# 🚀 서버 실행 방법

> 노션: [https://www.notion.so/suhodang/Back_-2afcc5b2d342806ea96fd78818764781](https://www.notion.so/suhodang/Back_-2afcc5b2d342806ea96fd78818764781)
- 아래에서 **macOS / Windows** 를 클릭하여 필요한 설치 방법만 확인하세요.

---

## 🔧 1. 환경 설정

<details>
<summary><strong>macOS</strong></summary>

### 1) 가상 환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) 라이브러리 설치

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>Windows</strong></summary>

### 1) 가상 환경 생성 및 활성화

```bash
python -m venv venv
venv\Scripts\activate
```

### 2) 라이브러리 설치

```bash
pip install -r requirements.txt
```

</details>

---

## 🗄️ 2. MariaDB 데이터베이스 설정

<details>
<summary><strong>macOS</strong></summary>

### 1) MariaDB 설치 및 실행 (Homebrew)

```bash
brew install mariadb
brew services start mariadb
```

### 2) 데이터베이스 생성

MariaDB 접속:

```bash
mysql -u root -p
```

DB 생성:

```sql
CREATE DATABASE soncoding_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

</details>

<details>
<summary><strong>Windows</strong></summary>

### 1) MariaDB 설치

👉 다운로드: [https://mariadb.org/download/](https://mariadb.org/download/)

설치 후 "Start MariaDB Service" 체크하여 자동 실행되도록 설정합니다.

### 2) MariaDB 접속

```cmd
mysql -u root -p
```

### 3) 데이터베이스 생성

```sql
CREATE DATABASE soncoding_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

</details>

---

## 🔐 3. `.env` 파일 설정

프로젝트 루트 경로에 `.env` 파일을 생성 후, 아래 내용을 채웁니다.

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YourNewPassword     # MariaDB root 비밀번호
DB_NAME=soncoding_db
GEMINI_API_KEY=YourGeminiApiKey # Gemini API 키
```

---

## 🚀 4. FastAPI 서버 실행

<summary><strong>macOS / Windows 공통</strong></summary>

루트 디렉토리에서 실행:

```bash
uvicorn main:app --reload
```

서버가 시작되면 `initialize_database()`가 자동 실행되어
테이블 및 초기 데이터가 생성됩니다.

정상 실행 메시지:

```
Uvicorn running on http://127.0.0.1:8000
```
