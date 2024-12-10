from langchain_community.document_loaders import DirectoryLoader
from ragas.llms import LangchainLLMWrapper
from langchain_groq.chat_models import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
model =ChatGroq(
        model_name="llama3-8b-8192",
        api_key="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",
        temperature=0.7,
       
    )
generator_embeddings = HuggingFaceEmbeddings()
generator_llm = LangchainLLMWrapper(model)
path = "Sample_Docs_Markdown/"
loader = DirectoryLoader(path, glob="**/*.md")
docs = loader.load()
from ragas.testset import TestsetGenerator
generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
dataset = generator.generate_with_langchain_docs(docs, testset_size=10)