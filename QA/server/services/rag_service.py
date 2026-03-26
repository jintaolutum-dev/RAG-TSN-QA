"""
Core RAG QA service
Builds a Retrieval-Augmented Generation (RAG) QA chain based on LangChain
Uses a large language model for answer generation
"""
from flask import current_app
# from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from services.vector_service import VectorService
from langchain_openai import ChatOpenAI


# RAG system prompt template
SYSTEM_PROMPT = """You are a knowledge-based question answering system focused on 
                TSN (Time-Sensitive Networking) in the field of industrial communication. 
                Please analyze and answer user questions rigorously based on the provided reference materials.

Constraints:

    All conclusions must be derived strictly from the reference materials; do not introduce external knowledge or subjective assumptions.
    If the reference materials are insufficient to answer the question, explicitly state that the information is missing.
    The response should be well-structured, use proper technical terminology, and follow an engineering or academic style.
    When necessary, quote key sentences from the reference materials to support your conclusions.

Reference materials:
{context}
"""

# User question template
USER_PROMPT = "{question}"


class RAGService:
    """RAG QA service class"""

    def __init__(self):
        """Initialize LLM and vector service"""
        api_key = current_app.config.get('OPENAI_API_KEY', '').strip()
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError(
                'OPENAI_API_KEY is not configured. Please set OPENAI_API_KEY in QA/server/.env'
            )

        # self.llm = ChatOllama(
        #     model=current_app.config['OLLAMA_LLM_MODEL'],
        #     base_url=current_app.config['OLLAMA_BASE_URL'],
        #     temperature=0.3,
        #     timeout=3600
        # )
        
        self.llm = ChatOpenAI(
            model=current_app.config['OPENAI_LLM_MODEL'],
            openai_api_key=api_key,
            base_url=current_app.config['OPENAI_BASE_URL'],
            temperature=0.3,
            timeout=3600
        )

        self.vector_service = VectorService()

    def _format_docs(self, docs):
        """
        Format retrieved documents into context text
        :param docs: List of retrieved documents
        :return: Formatted context text
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('file_name', 'Unknown source')
            formatted.append(f"[Source {i}: {source}]\n{doc.page_content}")
        return '\n\n'.join(formatted)

    def _extract_source_docs(self, docs):
        """
        Extract reference source information
        :param docs: List of retrieved documents
        :return: Source metadata list
        """
        sources = []
        seen = set()
        for doc in docs:
            file_name = doc.metadata.get('file_name', 'Unknown')
            if file_name not in seen:
                seen.add(file_name)
                sources.append({
                    'file_name': file_name,
                    'content': doc.page_content[:200]
                })
        return sources

    def ask(self, question, kb_id):
        """
        Main RAG QA method
        Flow: user question -> vector retrieval -> context build -> LLM answer generation
        :param question: User question
        :param kb_id: Knowledge base ID
        :return: (answer text, source list)
        """
        # Get retriever for the knowledge base
        retriever = self.vector_service.get_retriever(kb_id)

        # Retrieve relevant documents
        docs = retriever.invoke(question)

        if not docs:
            return 'Sorry, no relevant information related to your question was found in the knowledge base. Please try rephrasing your question.', []

        # Build prompt
        prompt = ChatPromptTemplate.from_messages([
            ('system', SYSTEM_PROMPT),
            ('human', USER_PROMPT)
        ])

        # Build RAG chain: retrieve -> format context -> prompt -> LLM -> parse output
        rag_chain = (
            {
                'context': lambda x: self._format_docs(docs),
                'question': RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        # Execute QA
        answer = rag_chain.invoke(question)

        # Extract source references
        source_docs = self._extract_source_docs(docs)

        return answer, source_docs

