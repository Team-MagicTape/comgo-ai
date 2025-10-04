import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
if os.getenv("OPENAI_API_KEY") is None:
    print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    exit()

FAISS_INDEX_PATH = "faiss_index"

def build_vector_store():
    """지정된 URL에서 문서를 로드하고, 청크로 분할한 다음,
    FAISS 벡터 스토어를 빌드하고 로컬에 저장합니다."""
    print("지식 베이스 구축을 시작합니다...")

    # 1. URL 목록 생성
    urls = [f"https://comgo.dev/articles/{i}" for i in range(2, 100)]
    print(f"{len(urls)}개의 URL에서 데이터 로드를 시도합니다.")

    # 2. WebBaseLoader를 사용하여 문서 로드
    # continue_on_failure=True: 로드 실패 시에도 중단하지 않고 계속 진행
    loader = WebBaseLoader(web_paths=urls, continue_on_failure=True)
    docs = loader.load()
    print(f"성공적으로 로드된 문서 수: {len(docs)}")

    if not docs:
        print("로드된 문서가 없습니다. 지식 베이스 구축을 중단합니다.")
        return

    # 3. 문서를 청크로 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"문서를 {len(splits)}개의 청크로 분할했습니다.")

    # 4. OpenAI 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings()

    # 5. FAISS 벡터 스토어 생성
    print("FAISS 벡터 스토어 생성을 시작합니다. 이 작업은 다소 시간이 걸릴 수 있습니다...")
    vector_store = FAISS.from_documents(splits, embeddings)
    print("벡터 스토어 생성 완료.")

    # 6. 벡터 스토어를 로컬에 저장
    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"벡터 스토어를 '{FAISS_INDEX_PATH}' 경로에 성공적으로 저장했습니다.")

if __name__ == "__main__":
    build_vector_store()
