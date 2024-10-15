from services import KnowledgeGraphService
import os

def setup_graph_db():
    # Initialize the KL
    kl_obj = KnowledgeGraphService()
    
    # Load and index the policy documents
    kl_obj.fill_knowledge_graph("./policies/")

if __name__ == "__main__":
    # Ensure OpenAI API key is set in the environment variables
    if "OPENAI_KEY" not in os.environ:
        raise EnvironmentError("Please set the OPENAI_KEY environment variable.")
    
    setup_graph_db()
