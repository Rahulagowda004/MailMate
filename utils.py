import os
import shutil
import re
from datetime import datetime
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from pathlib import Path
from datetime import datetime

def cleanup_datetime_folders(base_path="artifacts/embeddings", keep_count=1):
    
# current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
# persist_directory = rf"artifacts/embeddings/{current_datetime}"

# os.makedirs(persist_directory, exist_ok=True)
    """
    Delete oldest datetime-named folders, keeping only the most recent ones.
    Only processes folders matching the YYYYMMDD_HHMMSS pattern.
    """
    embeddings_path = Path(base_path)
    
    if not embeddings_path.exists():
        return
    
    # Pattern to match datetime folders (YYYYMMDD_HHMMSS)
    datetime_pattern = re.compile(r'^\d{8}_\d{6}$')
    
    # Get directories matching the datetime pattern
    datetime_dirs = [
        d for d in embeddings_path.iterdir() 
        if d.is_dir() and datetime_pattern.match(d.name)
    ]
    
    if len(datetime_dirs) <= keep_count:
        return
    
    # Sort by folder name (which is datetime format, so lexicographic sort works)
    datetime_dirs.sort(key=lambda x: x.name, reverse=True)
    
    # Delete old folders
    folders_to_delete = datetime_dirs[keep_count:]
    
    for folder in folders_to_delete:
        try:
            shutil.rmtree(folder)
            print(f"Deleted old embedding folder: {folder.name}")
        except Exception as e:
            print(f"Failed to delete {folder.name}: {e}")
            
def get_embeddings(pdf_path: Path, embeddings):

    # Safety measure I have put for debugging purposes :)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    pdf_loader = PyPDFLoader(pdf_path)# This loads the PDF
    # Checks if the PDF is there
    try:
        pages = pdf_loader.load()
    except Exception as e:
        print(f"Error loading PDF: {e}")
        raise
    # Chunking Process
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    pages_split = text_splitter.split_documents(pages) # We now apply this to our pages
    
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    persist_directory = rf"artifacts/embeddings/{current_datetime}"
    collection_name = r"resume"
    
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
    try:
        vectorstore = Chroma.from_documents(
            documents=pages_split,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        print(f"Created ChromaDB vector store!")
        
    except Exception as e:
        print(f"Error setting up ChromaDB: {str(e)}")
        raise
    return vecto