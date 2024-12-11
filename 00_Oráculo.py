import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader as web

from langchain_groq import ChatGroq

TIPOS_ARQUIVOS_VALIDOS = [
    'Glossário Marketing', 
    'Livro Top Secret - Cientista', 
    'Livro Cientista do Marketing',
    'Processo GT'
]

CONFIG_MODELOS = {'Groq': 
                        {'modelos': 'gemma2-9b-it',
                         'chat': ChatGroq}
                         }

MEMORIA = ConversationBufferMemory()

def carrega_site(url):
    loader = web(url)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento


def carrega_arquivos(tipo_arquivo, arquivo):
        documento = carrega_site(arquivo)

def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo):
    system_message = f'''Você é um assistente amigável chamado Oráculo.
Você possui acesso às seguintes informações vindas 
de um documento {tipo_arquivo}: 

####
{arquivo}
####

Utilize as informações fornecidas para basear as suas respostas.

Sempre que houver $ na sua saída, substita por S.

Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
sugira ao usuário carregar novamente o Oráculo!'''

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat

    st.session_state['chain'] = chain

def pagina_chat():
    st.markdown(f'<h2 style="text-align: center;">🤖Bem-vindo ao Oráculo</h2>', unsafe_allow_html=True)
    st.divider()

    chain = st.session_state.get('chain')
    if chain is None:
        st.error('Carregue o Oráculo')
        st.stop()

    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input('Fale com o oráculo')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chain.stream({'input': input_usuario,'chat_history': memoria.buffer_as_messages}))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria


def sidebar():
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione a Base de Conhecimento', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'Glossário Marketing':
            arquivo = 'https://vendas.v4company.com/glossario-marketing/'
        if tipo_arquivo == 'Livro Cientista do Marketing':
            arquivo = 'https://heyzine.com/flip-book/87da189f45.html'
        if tipo_arquivo == 'Livro Top Secret - Cientista':
            arquivo = 'https://heyzine.com/flip-book/d33a44284a.html'
        if tipo_arquivo == 'Processo GT':
            arquivo = 'Processo GT'
    with tabs[1]:
        st.markdown(f'<h5 style="text-align: center;">IA: Groq </h5>', unsafe_allow_html=True)
        provedor = 'Groq'

        st.markdown(f'<h5 style="text-align: center;">Modelo da IA: gemma2-9b-it </h5>', unsafe_allow_html=True)
        modelo = 'gemma2-9b-it'

        st.markdown(f'<h5 style="text-align: center;">Api do {provedor} ja inserida </h5>', unsafe_allow_html=True)
        api_key = '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'
        
        st.session_state[f'api_key_{provedor}'] = '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'
    
    if st.button('Inicializar Oráculo', use_container_width=True):
        carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo)
    if st.button('Apagar Histórico de Conversa', use_container_width=True):
        st.session_state['memoria'] = MEMORIA
    carrega_arquivos(tipo_arquivo, arquivo)


def main():
    with st.sidebar:
        sidebar()
    pagina_chat()


if __name__ == '__main__':
    main()
