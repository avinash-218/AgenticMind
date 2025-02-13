import os
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from prompts import context, code_parser_template
from code_reader import code_reader
from dotenv import load_dotenv
import ast

# Load environment variables from a .env file
load_dotenv()

# Initialize the language model with the 'mistral' model and a request timeout of 30 seconds
llm = Ollama(model='mistral')  # Ollama is used to interact with LLM (Large Language Models), 'mistral' is a model choice.

# Initialize a parser to handle markdown results
parser = LlamaParse(result_type='markdown')

# Define a file extractor for .pdf files using the parser
file_extractor = {".pdf": parser}  # Define the file types you want to handle. Here, it's for .pdf files.

# Load documents from the './data' directory using the file extractor
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# Resolve the embedding model to be used for document embeddings
embed_model = resolve_embed_model("local:BAAI/bge-m3")  # Load a pre-trained embedding model for document processing.

# Create a vector index from the loaded documents using the embedding model
vector_index = VectorStoreIndex.from_documents(documents=documents, embed_model=embed_model)

# Create a query engine from the vector index using the language model
query_engine = vector_index.as_query_engine(llm=llm)

# Define tools for the agent, including a query engine tool with metadata
tools = [
    QueryEngineTool(query_engine=query_engine,  # Create a query tool that interacts with the vector store.
        metadata=ToolMetadata(
            name="api_documentation",  # Naming the tool for clarity.
            description='this give doc about code for an api'  # Description of what the tool does.
        )),
    code_reader  # Another tool, presumably for reading and processing code.
]

# Initialize another language model for code-related tasks
code_llm = Ollama(model="codellama")  # A specialized LLM model for code-related queries.

# Create a ReActAgent using the defined tools, language model, and context
agent = ReActAgent.from_tools(tools=tools, llm=code_llm, verbose=False, context=context)

class CodeOutput(BaseModel):
    # Pydantic model to structure the output of the agent into a clean format.
    code: str  # The generated code.
    description: str  # The description or explanation of the code.
    filename: str  # The name of the file that will be created with the code.

# Initialize the output parser based on the Pydantic model
parser = PydanticOutputParser(CodeOutput)

# Define a template for the prompt, formatting the code parser into a string that can be used in the pipeline.
json_prompt_str = parser.format(code_parser_template)

# Create the actual prompt template
json_prompt_template = PromptTemplate(json_prompt_str)

# Create a query pipeline that chains the prompt template and language model
output_pipeline = QueryPipeline(chain=[json_prompt_template, llm])

# Main loop to interact with the agent
while(prompt:= input("Enter a prompt (q to quit): ")) != 'q':
    retries = 0  # Initialize retry counter

    while retries < 3:  # Retry logic in case of an error
        try:
            # Query the agent with the user's prompt and print the result
            result = agent.query(prompt)
            next_result = output_pipeline.run(result)
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))  # Clean the result into a valid Python dictionary
            break
        except Exception as e:  # If an error occurs, retry up to 3 times
            retries+=1
            print(f'Error Occured, Retry #{retries}:', {e})
        
    if retries >= 3:  # If 3 retries fail, print an error message and continue to next prompt.
        print("Unable to process request, try again...")
        continue

    # Print out the generated code and description
    print('Code Generated')
    print(cleaned_json['code'])
    print("\n\nDescription:", cleaned_json['description'])

    # Extract the filename from the response
    filename = cleaned_json['filename']

    try:
        # Attempt to save the generated code into a file in the "output" directory
        with open(os.path.join("output", filename), "w") as f:
            f.write(cleaned_json['code'])

        print('Saved file', filename)
    except:  # If saving the file fails, print an error message
        print("Error saving file")
