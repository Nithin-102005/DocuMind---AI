import chromadb


# Persistent ChromaDB database
client = chromadb.PersistentClient(
    path="/app/chroma_data"
)


# Document collection
collection = client.get_or_create_collection(
    name="documind_documents"
)


def add_chunks(
    document_id: int,
    user_id: int,
    chunks: list[str]
):
    """
    Store document chunks in ChromaDB.
    """

    if not chunks:
        return

    ids = [
        f"document_{document_id}_chunk_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "user_id": user_id,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas
    )


def search_chunks(
    query: str,
    user_id: int,
    n_results: int = 3
):
    """
    Search only the current user's document chunks.
    """

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={
            "user_id": user_id
        }
    )

    return results