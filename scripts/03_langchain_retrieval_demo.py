from pathlib import Path
import json
import shutil

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def load_case_summary(case_summary_path):
    """
    Load the processed case summary JSON.

    This file was created from the segmentation mask.
    It contains tumor-region volumes and label information.
    """

    if not case_summary_path.exists():
        raise FileNotFoundError(
            f"Missing case summary file: {case_summary_path}\n"
            "Run this first:\n"
            "  python scripts/01_create_case_summary.py"
        )

    case_summary_text = case_summary_path.read_text(encoding="utf-8")
    case_summary = json.loads(case_summary_text)

    return case_summary


def load_markdown_documents(knowledge_base_folder):
    """
    Load all Markdown files from the curated knowledge base.

    Each Markdown file becomes one LangChain Document.
    The metadata stores the filename so we know where retrieved text came from.
    """

    if not knowledge_base_folder.exists():
        raise FileNotFoundError(
            f"Missing knowledge base folder: {knowledge_base_folder}\n"
            "Run this first:\n"
            "  python scripts/02_create_knowledge_base.py"
        )

    markdown_paths = sorted(knowledge_base_folder.glob("*.md"))

    if len(markdown_paths) == 0:
        raise RuntimeError(
            f"No Markdown files found in: {knowledge_base_folder}\n"
            "Run this first:\n"
            "  python scripts/02_create_knowledge_base.py"
        )

    documents = []

    for markdown_path in markdown_paths:
        markdown_text = markdown_path.read_text(encoding="utf-8")

        document = Document(
            page_content=markdown_text,
            metadata={
                "source_file": markdown_path.name,
                "source_path": str(markdown_path),
            },
        )

        documents.append(document)

    return documents


def split_documents_into_chunks(documents):
    """
    Split long Markdown documents into smaller chunks.

    RAG usually retrieves chunks, not entire documents.
    Small chunks make retrieval more focused.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


def create_embedding_model():
    """
    Create a local Hugging Face sentence-transformer embedding model.

    This model converts text into vectors.
    Chroma stores those vectors and uses them for semantic search.
    """

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embedding_model


def rebuild_chroma_vector_store(chunks, embedding_model, vector_db_folder):
    """
    Build a Chroma vector database from the knowledge-base chunks.

    For learning simplicity, this script deletes and rebuilds the vector DB
    every time. This avoids duplicate chunks when the script is run repeatedly.
    """

    if vector_db_folder.exists():
        shutil.rmtree(vector_db_folder)

    vector_db_folder.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(vector_db_folder),
        collection_name="curated_mri_knowledge",
    )

    return vector_store


def create_retrieval_query_from_case_summary(case_summary):
    """
    Create a retrieval query using information from case_summary.json.

    This query tells the retriever what context we need from the knowledge base.
    """

    label_statistics = case_summary["label_statistics"]

    tumor_region_names = []

    for region_name in label_statistics.keys():
        if region_name != "background":
            tumor_region_names.append(region_name)

    tumor_region_text = ", ".join(tumor_region_names)

    query = (
        "Explain this segmented glioblastoma MRI case. "
        "Retrieve context about T1, contrast-enhanced T1 or T1-Gd, T2, FLAIR, "
        "tumor segmentation labels, segmentation-derived tumor volumes, "
        "whole tumor, tumor core, and safety limitations. "
        f"The tumor regions in this case are: {tumor_region_text}."
    )

    return query


def retrieve_relevant_documents(vector_store, query, number_of_chunks):
    """
    Retrieve the most relevant chunks from the Chroma vector store.
    """

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": number_of_chunks,
        }
    )

    retrieved_documents = retriever.invoke(query)

    return retrieved_documents


def save_retrieved_context(output_path, query, retrieved_documents):
    """
    Save retrieved chunks into a text file.

    The next RAG-report script can use this retrieved context.
    """

    output_lines = []

    output_lines.append("RETRIEVAL QUERY")
    output_lines.append("=" * 80)
    output_lines.append(query)
    output_lines.append("")

    output_lines.append("RETRIEVED CONTEXT")
    output_lines.append("=" * 80)

    for index, document in enumerate(retrieved_documents, start=1):
        source_file = document.metadata["source_file"]

        output_lines.append(f"[Chunk {index}] Source: {source_file}")
        output_lines.append("-" * 80)
        output_lines.append(document.page_content)
        output_lines.append("")

    output_text = "\n".join(output_lines)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")


def print_retrieval_results(query, retrieved_documents, output_path):
    """
    Print a readable summary of retrieved chunks.
    """

    print("=" * 80)
    print("LangChain retrieval demo")
    print("=" * 80)

    print("Retrieval query:")
    print(query)
    print()

    print(f"Number of retrieved chunks: {len(retrieved_documents)}")
    print("-" * 80)

    for index, document in enumerate(retrieved_documents, start=1):
        source_file = document.metadata["source_file"]

        preview = document.page_content.replace("\n", " ")
        preview = preview[:300] + "..."

        print(f"Chunk {index}")
        print(f"Source: {source_file}")
        print(f"Preview: {preview}")
        print("-" * 80)

    print()
    print(f"Saved retrieved context to: {output_path}")
    print("=" * 80)


def main():
    project_root = Path(__file__).resolve().parents[1]

    case_id = "case_001"

    case_summary_path = (
        project_root
        / "data"
        / "processed"
        / f"{case_id}_summary.json"
    )

    knowledge_base_folder = (
        project_root
        / "knowledge_base"
        / "curated_notes"
    )

    vector_db_folder = (
        project_root
        / "data"
        / "vector_db"
        / "curated_mri_knowledge_chroma"
    )

    retrieved_context_path = (
        project_root
        / "outputs"
        / f"{case_id}_retrieved_context.txt"
    )

    case_summary = load_case_summary(case_summary_path)

    documents = load_markdown_documents(knowledge_base_folder)

    chunks = split_documents_into_chunks(documents)

    print("=" * 80)
    print("Building LangChain retrieval pipeline")
    print("=" * 80)
    print(f"Markdown documents loaded: {len(documents)}")
    print(f"Text chunks created: {len(chunks)}")
    print(f"Vector DB folder: {vector_db_folder}")
    print("=" * 80)
    print()

    embedding_model = create_embedding_model()

    vector_store = rebuild_chroma_vector_store(
        chunks=chunks,
        embedding_model=embedding_model,
        vector_db_folder=vector_db_folder,
    )

    query = create_retrieval_query_from_case_summary(case_summary)

    retrieved_documents = retrieve_relevant_documents(
        vector_store=vector_store,
        query=query,
        number_of_chunks=5,
    )

    save_retrieved_context(
        output_path=retrieved_context_path,
        query=query,
        retrieved_documents=retrieved_documents,
    )

    print_retrieval_results(
        query=query,
        retrieved_documents=retrieved_documents,
        output_path=retrieved_context_path,
    )


if __name__ == "__main__":
    main()