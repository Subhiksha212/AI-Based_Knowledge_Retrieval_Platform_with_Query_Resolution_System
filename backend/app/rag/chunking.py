from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str) -> list[str]:
    """
    Split extracted document text into smaller overlapping chunks.

    Args:
        text: Plain text received from extractor.py.

    Returns:
        A list of text chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_text(text)

    return chunks