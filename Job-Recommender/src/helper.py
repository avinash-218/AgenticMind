import fitz
import os
from langchain_groq import ChatGroq
from apify_client import ApifyClient
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
apify_client = ApifyClient(os.getenv('APIFY_API_KEY'))

def extract_text_from_pdf(uploaded_file):
    """Extract text from pdf file.

    Args:
        uploaded_file (str): Path to pdf file.

    Returns:
        str: Text from pdf file.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_llm(prompt, max_tokens=500):
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.5,
        max_tokens=max_tokens,
    )

    messages = [
        ("system", "You are a helpful assistant."),
        ("user", prompt),
    ]

    response = llm.invoke(messages)

    # Ensure only text is returned
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    elif hasattr(response, "content"):
        return response.content
    else:
        return str(response)
    
