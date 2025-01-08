import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader as web

from langchain_groq import ChatGroq

TIPOS_ARQUIVOS_VALIDOS = [
    'V4 Company',
    'Glossário Marketing', 
    'Livro Top Secret - Cientista', 
    'Livro Cientista do Marketing',
    'Docs'
]

CARGOS = {
    'Gestores de Projetos ou Accounts' : '''Responsáveis pelo planejamento, execução e acompanhamento de projetos. Atuam como ponto de contato entre a equipe interna e os clientes, garantindo que entregas sejam realizadas dentro do prazo e conforme as expectativas. Gerenciam recursos e cronogramas, e solucionam problemas para assegurar o sucesso dos projetos.''',
    'Gestores de Tráfego' : '''Focados em estratégias de mídia paga e orgânica, eles gerenciam campanhas publicitárias em plataformas como Google Ads, Facebook Ads, e outros canais de mídia. Trabalham para aumentar o tráfego qualificado e otimizar o ROI (Retorno sobre Investimento).''',
    'Analista de CRM' : '''Especialista em gerenciar as relações com clientes por meio de sistemas de CRM (Customer Relationship Management). É responsável por segmentar públicos, planejar campanhas e otimizar a jornada do cliente para aumentar retenção e engajamento.''',
    'Designers' : '''Criam materiais visuais, como peças gráficas, layouts de sites, posts para redes sociais e outros ativos visuais. Trabalham para garantir que a comunicação visual esteja alinhada com a identidade da marca e os objetivos estratégicos.''',
    'Copywriters' : '''Especialistas em redação persuasiva. Criam textos para anúncios, e-mails, páginas de vendas, blogs e outros materiais, com foco em atrair, engajar e converter leads.''',
    'Analista de UX/UI' : '''Responsável pela experiência do usuário (UX) e design de interface do usuário (UI). Conduz pesquisas, testes e análises para garantir que produtos digitais sejam funcionais, intuitivos e esteticamente agradáveis.''',
    'Analista de Site' : '''Cuida da manutenção, performance e otimização de sites. Garante que o site esteja funcional, seguro e rápido, além de implementar melhorias baseadas em dados de análise de desempenho.''',
    'Head' : '''Gestor da vertente ou da equipe, responsável por liderar e gerenciar o time. Define estratégias, alinha metas, supervisiona as entregas e garante que os objetivos da equipe estejam alinhados com os objetivos gerais da empresa. Atua como um elo entre a alta gestão e os membros do time.''',
    'CAP' : '''Profissional que auxilia a vertente ou o time, proporcionando suporte estratégico e operacional. Trabalha em conjunto com o Head e a equipe para garantir a execução eficiente das tarefas, contribuindo com insights e ações práticas para o sucesso do grupo''',
    'Analista de Growth' : '''Focado em identificar oportunidades de crescimento para o negócio. Trabalha com experimentos, otimizações e estratégias de aquisição e retenção de clientes para impulsionar resultados.''',
    'Closers' : '''Especialistas em vendas, responsáveis por finalizar negociações e converter leads em clientes. Possuem alta capacidade de persuasão e foco em alcançar metas comerciais.''',
    'BDR (Business Development Representative)' : '''Profissionais focados em prospectar e qualificar leads para a equipe de vendas. Trabalham na geração de oportunidades e no fortalecimento de relacionamentos comerciais.''',
    'Financeiro' : '''Gerencia os recursos financeiros da empresa. Cuida do fluxo de caixa, orçamentos, pagamento de contas, faturamento e planejamento financeiro.''',
    'People & Performance' : '''Área responsável por cuidar das pessoas da empresa. Atua em recrutamento, treinamento, desenvolvimento de colaboradores e gestão de desempenho, promovendo um ambiente de trabalho saudável e produtivo.''',
    'Analista de BI (Business Intelligence)' : '''Responsável por coletar, organizar e analisar dados para fornecer insights estratégicos que apoiem a tomada de decisão. Cria dashboards, relatórios e análises que ajudam a empresa a identificar tendências, medir resultados e otimizar processos. Trabalha em estreita colaboração com outros times para garantir que os dados sejam utilizados de forma eficaz para atingir os objetivos da empresa.'''
}

CONFIG_MODELOS = {'Groq': 
                        {'modelos': 'llama-3.3-70b-versatile',
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
    system_message = f'''Você é um assistente amigável chamado Oráculo que é utilizada pela empresa v4 ferraz piai & CO.
Você possui acesso às seguintes informações vindas 
de um documento {tipo_arquivo}: 

####
{arquivo}
####

Utilize as informações fornecidas para basear as suas respostas, você não pode procurar por informações fora de seus documentos dispolibilizados e pode passar o links de seu documento enviando somente 1 link por resposta.

Utilize de respostas exatamente coerentes com o seu {arquivo}, preciso que quando algo que tenha no arquivo vc responda igualzinho o arquivo, utilizando o contexto para responder igualmente seus {arquivo} disponiveis.

Na empresa temos alguns nomenclaturas de cargos que vc desconhece, todos os nomes que vc tem que conhecer está em {CARGOS}.

Sempre que houver $ na sua saída, substita por R$.

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
        st.markdown(f'<h6 style="text-align: center;">Para evitar erros, envie uma mensagem como "olá" para inicializar a memória do chat.</h6>', unsafe_allow_html=True)
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
    tabs = st.tabs(['Upload de Arquivos', 'Modelo da IA'])
    with tabs[0]:
        st.markdown(f'<h5 style="text-align: center;">Inteligência V4 Ferraz Piai & CO 1.0 </h5>', unsafe_allow_html=True)
        tipo_arquivo = TIPOS_ARQUIVOS_VALIDOS
        arquivo = ['https://vendas.v4company.com/glossario-marketing/',
                    'https://heyzine.com/flip-book/87da189f45.html',
                    'https://heyzine.com/flip-book/d33a44284a.html',
                    'https://v4company.com/', 
                    'https://v4-ferraz.notion.site/Rotina-Ideal-de-um-Gestor-de-Tr-fego-a0a00d187619424ea1c165bb79ab4370?pvs=4',
                    'https://v4-ferraz.notion.site/E-com-do-Zero-ea94125e090b41ca995855e10417ed3c?pvs=4',
                    'https://v4-ferraz.notion.site/Retail-Varejo-ecbb0b331ea44923a922448916ba66a0?pvs=4',
                    'https://v4-ferraz.notion.site/Ferramentas-b0f25ce99d9b49c5a5a35e6e7629bf0c?pvs=4',
                    'https://v4-ferraz.notion.site/Account-Planning-04dd398c0cdf427db11983c366447c23?pvs=4',
                    'https://v4-ferraz.notion.site/Checklist-para-Auditoria-de-Ferramentas-547a51ed9f754f05ab0c9ad70dc96f4b?pvs=4',
                    'https://v4-ferraz.notion.site/Distribui-o-de-M-dia-Estrat-gias-2-4565b7a4f87649e383c1bed17ed3a505?pvs=4',
                    'https://v4-ferraz.notion.site/Rotinas-168ed1e2971442fabd9d48988fed3202?pvs=4',
                    'https://v4-ferraz.notion.site/Padr-o-de-UTMs-01b41041e864469ab047b5a29b76b512?pvs=73',
                    'https://v4-ferraz.notion.site/V4-Ferraz-Comece-por-aqui-53b9d81566af46a481dc0c94018035ef?pvs=74',
                    'https://v4-ferraz.notion.site/O-que-Landing-page-535b27ede8ee4c1e9f3090426f4462c8',
                    'https://v4-ferraz.notion.site/Conhe-a-o-processo-Growth-Pages-bebc53c87cb74e7f82e836ad60946824',
                    'https://v4-ferraz.notion.site/FAQ-78d055e854e94e2eaf981d57396a9848',
                    'https://v4-ferraz.notion.site/POP-Projeto-E-commerce-f8ef392897a044f2945e1dcccd6ba1e4',
                    'https://v4-ferraz.notion.site/POP-Wordpress-Institucional-4038e0c6b8e243228e73c2d34e7715b0',
                    'https://v4-ferraz.notion.site/O-que-an-lise-de-CRO-d5867f05743c4feba011491d97b89a14',
                    'https://v4-ferraz.notion.site/Conhe-a-a-cadeira-b9fede146ef1465e8be8ddf0dc13b1ca',
                    'https://v4-ferraz.notion.site/O-que-CRM-8f4a9412a4ad4377a0b05dacb7d6ae3a',
                    'https://v4-ferraz.notion.site/Quais-s-o-as-tarefas-padr-es-de-CRM-82536083096c4a60870737b5159037e1',
                    'https://v4-ferraz.notion.site/Como-implementar-um-CRM-77fc1d1881594ab58c496e8a8d744d6a',
                    'https://v4-ferraz.notion.site/Modelo-de-Debriefing-f5a2869027bc41199ed330ca69423245',
                    'https://v4-ferraz.notion.site/O-que-uma-Automa-o-461ffaf6e0194b1c8b4dfad29013b806',
                    'https://v4-ferraz.notion.site/Checklist-d8ab4fe3e79647849bb55915ad60be7a',
                    'https://v4-ferraz.notion.site/Otimizando-uma-Campanha-no-Meta-Ads-ad457dbab0094fcf936f4c02e3800596',
                    'https://v4-ferraz.notion.site/Auditoria-Gest-o-de-Tr-fego-em-Meta-Ads-1d8f4687cb7f49bd918a57fc8ab818b5',
                    'https://v4-ferraz.notion.site/Auditoria-Gest-o-de-Tr-fego-em-Google-Ads-24200a7c16a14709891e3b9234adb222',
                    'https://v4-ferraz.notion.site/Auditoria-Design-724d6b15549c47d2a790d7592934c3bb',
                    'https://v4-ferraz.notion.site/Auditoria-Social-Media-b88d360958244502b356a8ff60cb604c',
                    'https://v4-ferraz.notion.site/Auditoria-CRM-792e10e658484774aca9e3abfde8b1a7',
                    'https://v4-ferraz.notion.site/Campanhas-para-Google-My-Business-7f5ac80c423a464b8a6842e0578e1ecb',
                    'https://v4-ferraz.notion.site/Auditoria-Gest-o-de-Projeto-637e2ab0284c40a1b7a27d728589f8ec',
                    'https://v4-ferraz.notion.site/Padr-o-de-Nomenclatura-das-Auditorias-8cb1f0c989934062a922ef1fd8454989',
                    'https://v4-ferraz.notion.site/Subindo-Campanha-de-Cadastro-Lead-Nativo-3d11a98d98ee4b968c2958f8e8bb20f5',
                    'https://v4-ferraz.notion.site/00-Estudo-da-Ind-stria-e6ccae75499540d1be30ec703ba98f31',
                    'https://v4-ferraz.notion.site/02-Playbook-de-Tr-fego-67c6debd08ca4c8d92cec9c0d494c1be',
                    'https://v4-ferraz.notion.site/03-Playbook-de-Criativos-7265fdd5f02a4b0a89539f23caa3b86c',
                    'https://v4-ferraz.notion.site/04-Playbooks-Landing-Page-3fd3797c4b4644e08e13ebc5ad29f312',
                    'https://v4-ferraz.notion.site/05-Playbook-de-Estrat-gias-4497c444c49843be8ab21ab9d21a4bb9',
                    'https://v4-ferraz.notion.site/06-Playbook-de-Vendas-6e438418c93546a08c9a8c86e3deab49',
                    'https://v4-ferraz.notion.site/07-Metas-e-OKR-s-para-PDV-5b6c25e73cb24212af0266c3dd2a6df9',
                    'https://v4-ferraz.notion.site/Como-implementar-um-CRM-77fc1d1881594ab58c496e8a8d744d6a?pvs=4']
    with tabs[1]:
        st.markdown(f'<h5 style="text-align: center;">IA: Groq </h5>', unsafe_allow_html=True)
        provedor = 'Groq'

        st.markdown(f'<h5 style="text-align: center;">Modelo da IA: llama-3.3-70b-versatile </h5>', unsafe_allow_html=True)
        modelo = 'llama-3.3-70b-versatile'

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
