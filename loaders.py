from langchain_community.document_loaders import (WebBaseLoader,
                                                  YoutubeLoader,
                                                  CSVLoader,
                                                  PyPDFLoader,
                                                  TextLoader)

def carrega_site(url):
    loader = WebBaseLoader(url)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_youtube(video_id):
    loader = YoutubeLoader(video_id, add_video_info=False, language=['pt'])
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_csv(arquivo):
    loader = CSVLoader(arquivo)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_pdf(arquivo):
    loader = PyPDFLoader(arquivo)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_txt(arquivo):
    loader = TextLoader(arquivo)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento
