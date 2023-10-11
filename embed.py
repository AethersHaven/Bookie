from dotenv import load_dotenv
from os import getenv
from model import load_embeddings_model
from csv import DictReader
from ast import literal_eval
from langchain.schema.document import Document
from langchain.vectorstores import FAISS

def _load_books() -> list:
    """
    Load the books from a csv file and organize each book.

    Returns:
        list: A list of each book.
    """

    # Read books from file
    books = []
    with open('data\\books.csv', 'r', encoding='utf-8') as file:
        reader = DictReader(file)
        books = list(reader)

    # Convert each book into a string
    book_strings = []
    for book in books:
        author = None
        if len(book['authors']) > 3 and len(literal_eval(book['authors'])) > 0:
            author = literal_eval(book['authors'])[0]
        subjects = None
        if len(book['subjects']) > 3 and len(literal_eval(book['subjects'])) > 0:
            subjects = ', '.join(literal_eval(book['subjects']))

        synopsis = book['synopsis'] if len(book['synopsis']) > 0 else None

        summary = book['title'] if 'title' in book else "No Title"
        summary += f" by {author}\n" if author else "\n"
        summary += f"Subjects: {subjects}\n" if subjects else ""
        summary += f"Synopsis: {synopsis}" if synopsis else ""
        book_strings.append(summary)

    return [Document(page_content=book) for book in book_strings]

def embed_books():
    """
    Embed the books into a FAISS index and save it locally.
    """

    # Load environment variables
    load_dotenv()
    api_key = getenv('OPENAI_API_KEY')

    # Load embeddings model
    embeddings_model = load_embeddings_model("openai", api_key, max_retries=600)

    # Retrieve the books
    books = _load_books()

    # Embed the books into a FAISS index
    index = FAISS.from_documents(books, embeddings_model)

    # Save the FAISS index locally
    index.save_local("index")

def get_relevant_books(query: str, top_k: int) -> list:
    """
    Search the embedded books for relevant books based on the provided query.

    Args:
        query (str): The search query.
        top_k (int): The number of top relevant books to retrieve.

    Returns:
        list: A list of relevant books.
    """

    # Load environment variables
    load_dotenv()
    api_key = getenv('OPENAI_API_KEY')

    # Load embeddings model
    embeddings_model = load_embeddings_model("openai", api_key)

    # Load the FAISS index locally
    index = FAISS.load_local("index", embeddings_model)

    # Search the FAISS index for relevant books
    docs = index.similarity_search(query, top_k)

    return [doc.page_content for doc in docs]