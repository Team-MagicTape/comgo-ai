# CS 지식 튜터 챗봇

이 프로젝트는 LangChain과 FastAPI를 사용하여 구축된 컴퓨터 과학(CS) 지식 기반의 튜터 챗봇입니다.

사용자의 질문 의도를 파악하여, 지식 베이스에 기반한 정확한 답변을 제공하거나, 사용자의 오개념을 바로잡아주는 맞춤형 해설을 제공합니다.

## 주요 기능

- **RAG (검색 증강 생성):** 미리 구축된 CS 관련 지식 베이스를 검색하여, 사실에 기반한 답변을 생성합니다.
- **의도 분석 라우팅:** 사용자의 질문 유형(단순 질문, 오개념 해설 요청, 일반 대화)을 분석하여, 각 상황에 가장 적합한 방식으로 답변합니다.
- **실시간 답변 스트리밍:** Server-Sent Events (SSE)를 사용하여 AI의 답변을 실시간으로 스트리밍합니다.

## 기술 스택

- **Backend:** Python, FastAPI
- **AI:** LangChain, OpenAI API
- **Vector Store:** FAISS

## 설치 및 실행 방법

### 1. 프로젝트 복제

```bash
git clone [저장소 URL]
cd [프로젝트 폴더]
```

### 2. 환경 설정

- **`.env` 파일 생성:**
  `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 파일 내에 자신의 OpenAI API 키를 입력합니다.

  ```bash
  cp .env.example .env
  ```

- **가상환경 생성 및 활성화:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. 의존성 설치

`requirements.txt` 파일에 명시된 라이브러리들을 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. 지식 베이스 구축 (최초 1회)

`scripts/build_vector_store.py` 스크립트를 실행하여 RAG 챗봇이 사용할 벡터 데이터베이스를 생성합니다. 이 과정은 몇 분 정도 소요될 수 있습니다.

```bash
python3 scripts/build_vector_store.py
```

### 5. 서버 실행

`run.sh` 스크립트를 실행하여 FastAPI 서버를 시작합니다.

```bash
sh run.sh
```

서버가 시작되면, 웹 브라우저에서 `http://localhost:8000` 주소로 접속하여 챗봇을 사용할 수 있습니다.

## API 사용법 (SSE 스트리밍)

앱 등 다른 클라이언트에서 사용하기 위한 스트리밍 API 엔드포인트입니다.

- **URL:** `/api/chat`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "message": "사용자 질문"
  }
  ```
- **Response:** Server-Sent Events (SSE) 스트림

**`curl` 예시:**

```bash
curl -X POST http://localhost:8000/api/chat \
-H "Content-Type: application/json" \
-d '{"message": "캡슐화가 뭐야?"}'
```

## 프로젝트 구조

```
/
|-- app/                  # 애플리케이션 소스 코드
|   |-- main.py           # FastAPI 앱 정의, API 엔드포인트
|   |-- chains.py         # LangChain 체인 정의
|   |-- prompts.py        # 프롬프트 템플릿
|   |-- core/             # 핵심 설정 및 모델 초기화
|
|-- static/               # HTML 등 정적 파일
|   |-- index.html
|
|-- scripts/              # 일회성 스크립트
|   |-- build_vector_store.py
|
|-- faiss_index/          # 벡터 DB (자동 생성)
|-- venv/                 # 가상환경 (자동 생성)
|-- requirements.txt
|-- run.sh
|-- .env.example
|-- README.md
```
