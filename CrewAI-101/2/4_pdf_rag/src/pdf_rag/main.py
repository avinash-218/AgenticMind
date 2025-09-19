import sys
import warnings
sys.path.append('.')
from datetime import datetime
from src.pdf_rag.crew import PdfRag

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    user_input = input('Enter your prompt: ')
    inputs = {
        'input': user_input,
    }
    
    try:
        PdfRag().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

run()