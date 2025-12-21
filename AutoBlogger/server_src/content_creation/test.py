from dotenv import load_dotenv
load_dotenv()
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from server_src.content_creation.graph.graph import content_graph
from server_src.content_creation.utils import draw_stylish_graph

if __name__=='__main__':
    draw_stylish_graph(content_graph, output_name="content_graph")
    
    result = content_graph.invoke(input={"title":"Artificial General Intelligence"})
    if result['content']:
        print(f"Status: Success\Title:{result['title']}\nContent:{result['content']}")
    else:
        print(f"Status: Failed\nReason:{result['exit_reason']}")