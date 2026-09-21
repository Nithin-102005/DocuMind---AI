from app.services.vector_service import search_chunks


def retrieve_relevant_chunks(
    question: str,
    user_id: int,
    n_results: int = 5
):
    """
    Retrieve relevant document chunks
    belonging only to the current user.
    """

    results = search_chunks(
        query=question,
        user_id=user_id,
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        retrieved_chunks.append(
            {
                "content": document,
                "document_id": metadata["document_id"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance
            }
        )

    return retrieved_chunks


def build_context(
    chunks: list[dict]
) -> str:
    """
    Combine retrieved chunks into context
    for the LLM.
    """

    context_parts = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):
        context_parts.append(
            f"""
Source {index}
Document ID: {chunk["document_id"]}
Chunk: {chunk["chunk_index"]}

{chunk["content"]}
"""
        )

    return "\n\n".join(context_parts)
