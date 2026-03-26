"""
Project configuration file
Contains configuration for database, Ollama, Chroma, and more
"""
import os


def load_local_env():
    """Load key-value pairs from a local .env file into process env."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_local_env()


class Config:
    """Base configuration class"""

    # Flask secret key for JWT signing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'enterprise-qa-secret-key-2024')

    # MySQL configuration (port 3306, password 123456)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'db_enterprise_qa')

    # SQLAlchemy database connection URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT token expiration (seconds), default 24 hours
    JWT_EXPIRATION = 86400

    # Ollama configuration
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_LLM_MODEL = os.environ.get('OLLAMA_LLM_MODEL', 'qwen3:4b')
    OLLAMA_EMBED_MODEL = os.environ.get('OLLAMA_EMBED_MODEL', 'qwen3-embedding:4b')

    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_LLM_MODEL = os.environ.get('OPENAI_LLM_MODEL', 'gpt-4o-mini')
    OPENAI_EMBED_MODEL = os.environ.get('OPENAI_EMBED_MODEL', 'text-embedding-3-small')

    # ChromaDB persistent storage path
    CHROMA_PERSIST_DIR = os.environ.get(
        'CHROMA_PERSIST_DIR',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_data')
    )

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # Maximum upload file size: 50MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx'}

    # Document chunking configuration
    CHUNK_SIZE = 500        # Number of characters per chunk
    CHUNK_OVERLAP = 50      # Overlap characters between chunks

    # Vectorization batch configuration
    EMBED_BATCH_SIZE = 10   # Number of chunks sent per batch
    EMBED_MAX_RETRIES = 3   # Max retries for embedding failures

    # RAG retrieval configuration
    RETRIEVER_TOP_K = 4     # Number of similar documents returned by retrieval

