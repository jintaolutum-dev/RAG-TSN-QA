"""
Document vectorization service
Responsible for document parsing, text chunking, and Chroma vector storage
"""
import os
import time
from flask import current_app
# from ollama import Client as OllamaClient, ResponseError
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from langchain_openai import OpenAIEmbeddings

class OllamaServiceError(Exception):
    """Ollama service exception for clearer error messages"""
    pass


class VectorService:
    """Document vectorization service类"""

    def __init__(self):
        """Initialize embedding model and text splitter"""
        self.embeddings = OpenAIEmbeddings(
            model=current_app.config['OPENAI_EMBED_MODEL'],
            api_key=current_app.config['OPENAI_API_KEY'],
            base_url=current_app.config['OPENAI_BASE_URL']
        )
        # self.embeddings = OllamaEmbeddings(
        #     model=current_app.config['OLLAMA_EMBED_MODEL'],
        #     base_url=current_app.config['OLLAMA_BASE_URL']
        # )
        
        self.text_splitter = RecursiveCharacterTextSplitter( # pyright: ignore[reportUndefinedVariable]
            chunk_size=current_app.config['CHUNK_SIZE'],
            chunk_overlap=current_app.config['CHUNK_OVERLAP'],
            length_function=len
        )
        self.persist_dir = current_app.config['CHROMA_PERSIST_DIR']
        self.batch_size = current_app.config.get('EMBED_BATCH_SIZE', 10)
        self.max_retries = current_app.config.get('EMBED_MAX_RETRIES', 3)

    # def _check_ollama(self):
    #     """
    #     Pre-check Ollama service availability and embedding model readiness.
    #     Only hard-fail when the service is down or the model is not installed;
    #     transient 5xx errors are logged as warnings and handled by retries.
    #     :raises OllamaServiceError: raised when service is unreachable or model is not installed
    #     """
    #     base_url = current_app.config['OLLAMA_BASE_URL']
    #     model_name = current_app.config['OLLAMA_EMBED_MODEL']
    #     client = OllamaClient(host=base_url)

    #     try:
    #         model_list = client.list()
    #     except ConnectionError:
    #         raise OllamaServiceError(
    #             f'Cannot connect to Ollama service ({base_url}); please ensure Ollama is running'
    #         )
    #     except ResponseError as e:
    #         current_app.logger.warning(
    #             f'Ollama pre-check returned abnormal status ({e.status_code}); continue vectorization: {e}'
    #         )
    #         return
    #     except Exception as e:
    #         current_app.logger.warning(f'Ollama pre-check failed; continue vectorization: {e}')
    #         return

    #     installed = {m.get('name', '') for m in model_list.get('models', [])}
    #     if not any(model_name in name or name in model_name for name in installed):
    #         raise OllamaServiceError(
    #             f'Embedding model {model_name} is not installed. Run: ollama pull {model_name}'
    #         )

    def _get_collection_name(self, kb_id):
        """
        Generate Chroma collection name based on KB ID
        Each knowledge base uses an isolated collection
        """
        return f"kb_{kb_id}"

    def _load_file(self, file_path, file_type):
        """
        Load document content by file type
        :param file_path: File path
        :param file_type: File type (txt/pdf/md/docx)
        :return: Text content
        """
        text = ''
        if file_type in ('txt', 'md'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        elif file_type == 'pdf':
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

        elif file_type == 'docx':
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + '\n'

        return text

    def _add_texts_with_retry(self, vectorstore, texts, metadatas, ids):
        """
        Retryable vector writes to handle transient errors (502/503/504, etc.)
        :param vectorstore: Chroma vector store instance
        :param texts: Text chunk list
        :param metadatas: Metadata list
        :param ids: ID list
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
                return
            except Exception as e:
                last_error = e
                err_msg = str(e)
                is_retryable = any(code in err_msg for code in ('502', '503', '504'))
                if not is_retryable or attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt
                current_app.logger.warning(
                    f'Ollama嵌入请求失败(第{attempt + 1}次)，{wait}秒后重试: {err_msg}'
                )
                time.sleep(wait)
        raise last_error

    def process_document(self, doc_id, file_path, file_type, kb_id):
        """
        Process document: pre-check -> parse file -> split text -> batch write to vector store
        :param doc_id: Document ID
        :param file_path: File path
        :param file_type: File type
        :param kb_id: 知识库ID
        :return: Number of chunks
        """
        # self._check_ollama()

        text = self._load_file(file_path, file_type)
        if not text.strip():
            raise ValueError('Document content is empty; vectorization cannot proceed')

        chunks = self.text_splitter.split_text(text)
        if not chunks:
            raise ValueError('Document chunking failed')

        file_name = os.path.basename(file_path)
        metadatas = [{'doc_id': doc_id, 'file_name': file_name, 'chunk_index': i} for i in range(len(chunks))]
        ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]

        collection_name = self._get_collection_name(kb_id)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

        # Batch writes to reduce pressure per embedding request
        for i in range(0, len(chunks), self.batch_size):
            batch_end = min(i + self.batch_size, len(chunks))
            self._add_texts_with_retry(
                vectorstore,
                texts=chunks[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end],
            )

        return len(chunks)

    def delete_document(self, doc_id, kb_id):
        """
        Delete all chunks of the specified document from vector store
        :param doc_id: Document ID
        :param kb_id: 知识库ID
        """
        collection_name = self._get_collection_name(kb_id)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )
        # Filter by document ID and delete
        vectorstore._collection.delete(where={'doc_id': doc_id})

    def get_retriever(self, kb_id):
        """
        Get retriever for the specified knowledge base
        :param kb_id: 知识库ID
        :return: Chroma检索器
        """
        collection_name = self._get_collection_name(kb_id)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )
        return vectorstore.as_retriever(
            search_kwargs={'k': current_app.config['RETRIEVER_TOP_K']}
        )

