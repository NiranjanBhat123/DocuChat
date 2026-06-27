import logging

from documents.services.pdf_processor import PDFProcessor
from documents.services.chunker import TextChunker

from vector_store.services.embedder import Embedder
from vector_store.services.chroma import ChromaService



logger = logging.getLogger(__name__)


class DocumentIngestionService:


    def __init__(self):

        self.pdf_processor = PDFProcessor()

        self.chunker = TextChunker()

        self.embedder = Embedder()

        self.vector_store = ChromaService()



    def process(self, document):

        logger.info(
            f"Processing document {document.id}"
        )


        text = self.pdf_processor.extract_text(
            document.file.path
        )


        logger.info(
            "PDF text extracted"
        )


        chunks = self.chunker.split(
            text
        )


        logger.info(
            f"Created {len(chunks)} chunks"
        )


        embeddings = self.embedder.generate(
            chunks
        )


        logger.info(
            "Embeddings generated"
        )


        self.vector_store.add_chunks(
            chunks,
            embeddings
        )


        document.processed=True

        document.save()


        logger.info(
            "Document ingestion completed"
        )


        return document