import json
import os
from datetime import datetime

####################################################################
# NCAS — NÚCLEO COGNITIVO DA AURORA SIGER
#   Sistema de registro, consulta e interpretação de informações
# operacionais da colônia marciana Aurora Siger.
####################################################################


####################################################################
# 1. MANIPULAÇÃO DE ARQUIVOS
#   Dados estruturados ficam em JSON; registros sequenciais em TXT.
####################################################################

## Montando os caminhos dos arquivos de dados a partir da pasta deste arquivo
## __file__ é o caminho do próprio codigo_fonte.py, então o sistema encontra o JSON
## e o TXT mesmo quando é executado a partir de outra pasta
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_JSON = os.path.join(PASTA_BASE, "dados_colonia.json")
ARQUIVO_TXT = os.path.join(PASTA_BASE, "registros_colonia.txt")


## Criando uma função para ler o arquivo JSON inteiro
def carregar_dados(caminho):
    # Abrindo o arquivo JSON em modo leitura ("r")
    with open(caminho, "r", encoding="utf-8") as arquivo:
        # json.load converte o conteúdo do arquivo em estruturas Python
        dados = json.load(arquivo)
    # Retornar o dicionário com todas as seções do arquivo
    return dados


## Criando uma função para gravar o dicionário completo de volta no arquivo JSON
## O modo "w" reescreve o arquivo inteiro já com a estrutura atualizada
def salvar_dados(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        # json.dump faz o contrário do json.load: grava o dicionário como texto JSON
        # indent deixa o arquivo legível e ensure_ascii=False preserva os acentos
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


## Criando uma função para ler apenas a lista de módulos da colônia
def carregar_modulos(caminho):
    dados = carregar_dados(caminho)
    # Retornar a lista da chave "modulos"
    return dados["modulos"]


## Criando a função que adiciona registros no registros_colonia.txt ou cria o arquivo caso ele não exista
## O modo "a" (append) preserva o histórico; o modo "w" apagaria tudo a cada gravação
def gravar_registro(caminho, mensagem):
    # Abrindo o arquivo em modo append
    with open(caminho, "a", encoding="utf-8") as arquivo:
        # write() não pula linha sozinho, por isso o \n no final
        arquivo.write(mensagem + "\n")


## Criando a função para ler os registros
## Usamos TXT porque os registros são linhas sequenciais simples (log)
def ler_registros(caminho):
    # O modo "r" gera erro se o arquivo não existir, então verificamos antes
    if not os.path.exists(caminho):
        return []                    # retorna lista vazia se não existe
    with open(caminho, "r", encoding="utf-8") as arquivo:
        # readlines() devolve uma lista com todas as linhas do arquivo
        registros = arquivo.readlines()
    return registros


####################################################################
# 2. VALIDAÇÃO E BUSCA
####################################################################

## Função que vai verificar se o usuário está digitando um módulo válido
def validar_modulo(nome_modulo):
    modulos = carregar_modulos(ARQUIVO_JSON)

    for modulo in modulos:
        # .lower() nos dois lados torna a comparação insensível a maiúsculas
        if modulo["nome"].lower() == nome_modulo.lower():
            return True
    return False


####################################################################
# 3. REGRAS LÓGICAS
#   Expressão original:   ALERTA = NOT (ATIVO AND NOT RISCO_ALTO)
#   Aplicando De Morgan:  ALERTA = NOT ATIVO OR RISCO_ALTO
#   Forma simplificada:   ALERTA = INATIVO OR RISCO_ALTO
####################################################################

## Aplica a regra booleana simplificada para decidir se o módulo gera alerta
def gerar_alerta(modulo):
    # Verificar se está inativo
    inativo = modulo["status"] == "inativo"
    # Verificar se o risco é alto
    risco_alto = modulo["nivel_risco"] == "alto"
    # Retornar True se inativo OR risco alto
    return inativo or risco_alto


####################################################################
# 4. OPERAÇÕES DO SISTEMA
####################################################################

## Função para cadastrar novos registros
def cadastrar_registro():
    modulo = input("Digite o nome do módulo: ")

    # Só grava se o módulo existir na colônia
    if not validar_modulo(modulo):
        print("Módulo não encontrado! Os módulos são: Habitat Alpha, MedBase, Reator Solar, BioLab, LogiStore e TerraBot.")
        return

    mensagem = input("Digite o registro: ")

    # Registrando o horário do registro
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    registro = f"[{agora}] Módulo: {modulo} | Registro: {mensagem}"

    gravar_registro(ARQUIVO_TXT, registro)

    print("Registro salvo com sucesso!")


## Função para apagar registros
def apagar_registro(caminho):
    registros = ler_registros(caminho)

    # Saindo da função se não houver nada para apagar
    if len(registros) == 0:
        print("Não existem registros para apagar.")
        return

    # Exibe os registros numerados para o usuário escolher
    print("\nREGISTROS SALVOS:")
    # O start=1 começa a numeração em 1; o strip() remove o \n do final da linha
    for i, registro in enumerate(registros, start=1):
        print(f"{i} - {registro.strip()}")

    escolha = input("\nDigite o número do registro que deseja apagar: ")

    # Garante que o usuário digitou um número antes de converter
    if not escolha.isdigit():
        print("Digite um número válido.")
        return

    escolha = int(escolha)

    # Verifica se o número escolhido está dentro do intervalo existente
    if escolha < 1 or escolha > len(registros):
        print("Registro não encontrado.")
        return

    # pop remove o item da lista; -1 porque a lista começa em 0 e o menu em 1
    registros.pop(escolha - 1)

    # Modo "w" reescreve o arquivo inteiro com a lista já sem o registro removido
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.writelines(registros)

    print("Registro apagado com sucesso!")


## Função para apagar todo o histórico de registros
def limpar_registros(caminho):
    # Pede confirmação porque a operação é irreversível
    confirmacao = input("Tem certeza que deseja apagar todos os registros? (s/n): ")

    if confirmacao.lower() == "s":
        # Escrever string vazia em modo "w" zera o conteúdo do arquivo
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write("")

        print("Todos os registros foram apagados.")
    else:
        print("Operação cancelada.")


## Percorre todos os módulos e exibe os que a regra booleana marcou como alerta
def analisar_alertas():
    modulos = carregar_modulos(ARQUIVO_JSON)
    encontrou = False          # começa assumindo que não há alertas

    for modulo in modulos:
        # gerar_alerta aplica a expressão booleana simplificada
        if gerar_alerta(modulo):
            print(f"ALERTA: {modulo['nome']} — status: {modulo['status']} | risco: {modulo['nivel_risco']}")
            encontrou = True   # marca que achou pelo menos um

    # Só é verificado depois de percorrer todos os módulos
    if not encontrou:
        print("Nenhum módulo em situação de alerta.")


####################################################################
# 5. ENGENHARIA DE PROMPTS
#   Os três estilos pedem a mesma tarefa (classificar e relatar),
# mudando apenas a técnica: sem exemplos, com exemplos e com
# formato de saída definido.
####################################################################

## Prompt ZERO-SHOT: apenas a instrução, sem exemplos de referência
def prompt_zero_shot(modulo):
    prompt = f"""Você é o assistente do Núcleo Cognitivo da Aurora Siger (NCAS). Sua função é analisar a situação operacional dos módulos da colônia.

Módulo: {modulo['nome']}
Status: {modulo['status']}
Nível de risco: {modulo['nivel_risco']}
Consumo: {modulo['consumo_kwh']} kWh
Última manutenção: {modulo['ultima_manutencao']}

Classifique este módulo como "Normal", "Alerta" ou "Crítico" de acordo com a sua situação.
Em seguida, gere um relatório operacional de até 3 linhas contendo a justificativa da classificação, a ação recomendada ao centro de controle e o risco de não agir.
"""
    return prompt


## Prompt FEW-SHOT: os exemplos calibram o critério de classificação e fixam o formato da resposta
## Os módulos dos exemplos são fictícios de propósito: assim a resposta do módulo consultado
## é deduzida do padrão apresentado, e não copiada de um exemplo que já traz a resposta pronta
def prompt_few_shot(modulo):
    prompt = f"""Você é o assistente do Núcleo Cognitivo da Aurora Siger (NCAS). Sua função é analisar a situação operacional dos módulos da colônia.

Classifique o módulo como "Normal", "Alerta" ou "Crítico" e gere um relatório operacional de até 3 linhas contendo a justificativa da classificação, a ação recomendada ao centro de controle e o risco de não agir.

Siga os exemplos abaixo:

EXEMPLO 1
Módulo: Estufa Norte | Status: ativo | Risco: baixo | Consumo: 18.0 kWh | Última manutenção: 2026-05-20
Classificação: Normal
Relatório: Módulo em operação regular, sem indicadores de risco. Nenhuma ação imediata é necessária. Manter o monitoramento de rotina.

EXEMPLO 2
Módulo: Central Hídrica | Status: ativo | Risco: medio | Consumo: 27.0 kWh | Última manutenção: 2026-03-04
Classificação: Alerta
Relatório: Módulo operacional, porém com risco moderado. Recomenda-se agendar inspeção preventiva. Sem intervenção, o risco tende a aumentar.

EXEMPLO 3
Módulo: Oficina Robótica | Status: inativo | Risco: alto | Consumo: 51.0 kWh | Última manutenção: 2026-01-12
Classificação: Crítico
Relatório: Módulo fora de operação e com risco alto. Requer intervenção técnica imediata. A permanência do estado compromete a operação da colônia.

AGORA CLASSIFIQUE:
Módulo: {modulo['nome']} | Status: {modulo['status']} | Risco: {modulo['nivel_risco']} | Consumo: {modulo['consumo_kwh']} kWh | Última manutenção: {modulo['ultima_manutencao']}
"""
    return prompt


## Prompt STRUCTURED OUTPUT: define o formato exato da resposta para que o sistema possa processá-la
## As chaves aparecem dobradas ({{ }}) porque em f-string a chave simples indicaria uma variável
def prompt_structured(modulo):
    prompt = f"""Você é o assistente do Núcleo Cognitivo da Aurora Siger (NCAS). Sua função é analisar a situação operacional dos módulos da colônia.

Analise o módulo abaixo e responda APENAS com um objeto JSON válido, sem texto antes ou depois.

Módulo: {modulo['nome']}
Status: {modulo['status']}
Nível de risco: {modulo['nivel_risco']}
Consumo: {modulo['consumo_kwh']} kWh
Última manutenção: {modulo['ultima_manutencao']}

Use exatamente esta estrutura:
{{
    "modulo": "nome do módulo",
    "classificacao": "Normal | Alerta | Crítico",
    "justificativa": "motivo da classificação em uma frase",
    "acao_recomendada": "ação sugerida ao centro de controle",
    "prioridade_atendimento": 1
}}

A chave "prioridade_atendimento" deve ser um número inteiro de 1 a 5, onde 1 indica urgência máxima.
"""
    return prompt


####################################################################
# 6. SIMULAÇÃO DA IA GENERATIVA
#   A resposta é simulada localmente: a classificação vem da mesma
# regra booleana usada pelo sistema, sem chamada a API externa.
#   Cada estilo de prompt gera a resposta no formato que ele pediu,
# que é justamente o efeito que a técnica teria em um modelo real.
####################################################################

## Aplica o critério de classificação e devolve as informações que os prompts pedem
## Separar essa análise garante que os três estilos usem exatamente o mesmo raciocínio
def analisar_modulo(modulo):
    # A regra booleana simplificada define o caso mais grave
    if gerar_alerta(modulo):
        classificacao = "Crítico"
        prioridade = 1

        # Separa os dois motivos possíveis de alerta para justificar melhor
        if modulo["status"] == "inativo":
            justificativa = f"O módulo {modulo['nome']} está fora de operação e com nível de risco {modulo['nivel_risco']}."
        else:
            justificativa = f"O módulo {modulo['nome']} está em operação, mas com nível de risco alto."

        acao = "Acionar a equipe técnica para intervenção imediata."
        risco_de_nao_agir = "A permanência do estado compromete a operação da colônia."

    # Risco moderado não aciona a regra, mas ainda merece acompanhamento
    elif modulo["nivel_risco"] == "medio":
        classificacao = "Alerta"
        prioridade = 3
        justificativa = f"O módulo {modulo['nome']} está operacional, porém com nível de risco moderado."
        acao = "Agendar inspeção preventiva no próximo ciclo."
        risco_de_nao_agir = "Sem intervenção, a tendência é o quadro evoluir para crítico."

    # Nenhuma condição atendida: situação normal
    else:
        classificacao = "Normal"
        prioridade = 5
        justificativa = f"O módulo {modulo['nome']} está em operação regular, sem indicadores de risco."
        acao = "Nenhuma ação imediata é necessária."
        risco_de_nao_agir = "Manter o monitoramento de rotina."

    # Devolve um dicionário para os três formatos de resposta reaproveitarem os mesmos dados
    return {
        "modulo": modulo["nome"],
        "classificacao": classificacao,
        "justificativa": justificativa,
        "acao_recomendada": acao,
        "risco_de_nao_agir": risco_de_nao_agir,
        "prioridade_atendimento": prioridade
    }


## Monta a resposta que o assistente devolveria, no formato pedido pelo prompt enviado
def resposta_simulada(modulo, estilo):
    # O diagnóstico é o mesmo nos três estilos; o que muda é a apresentação
    analise = analisar_modulo(modulo)

    # ZERO-SHOT: sem exemplos para imitar, a resposta sai em texto corrido
    if estilo == "1":
        resposta = f"""Classificação: {analise['classificacao']}
Relatório: {analise['justificativa']} {analise['acao_recomendada']} {analise['risco_de_nao_agir']}"""

    # FEW-SHOT: os exemplos padronizam a saída, então ela repete o formato deles
    elif estilo == "2":
        resposta = f"""Módulo: {analise['modulo']}
Classificação: {analise['classificacao']}
Relatório: {analise['justificativa']} {analise['acao_recomendada']} {analise['risco_de_nao_agir']}"""

    # STRUCTURED OUTPUT: JSON válido, com exatamente as chaves exigidas pelo prompt
    else:
        # Monta o dicionário apenas com os campos que o prompt pediu
        saida = {
            "modulo": analise["modulo"],
            "classificacao": analise["classificacao"],
            "justificativa": analise["justificativa"],
            "acao_recomendada": analise["acao_recomendada"],
            "prioridade_atendimento": analise["prioridade_atendimento"]
        }
        # json.dumps faz o contrário do json.load: transforma o dicionário em texto JSON
        # ensure_ascii=False preserva os acentos e indent deixa a saída legível
        resposta = json.dumps(saida, indent=4, ensure_ascii=False)

    return resposta


## Guarda a resposta do assistente na lista "historico_interacoes" do arquivo JSON
## É o caminho inverso da leitura: o dicionário sai da memória e volta para o disco
def salvar_interacao(modulo, tecnica):
    # Carrega o arquivo inteiro, porque a gravação vai reescrevê-lo por completo
    dados = carregar_dados(ARQUIVO_JSON)

    # .get devolve a lista já existente ou uma lista vazia na primeira execução
    historico = dados.get("historico_interacoes", [])

    # A resposta é guardada em campos separados, e não como um texto único,
    # para que o próprio sistema consiga consultá-la depois
    analise = analisar_modulo(modulo)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")

    historico.append({
        "data": agora,
        "modulo": analise["modulo"],
        "tecnica": tecnica,
        "classificacao": analise["classificacao"],
        "justificativa": analise["justificativa"],
        "acao_recomendada": analise["acao_recomendada"],
        "prioridade_atendimento": analise["prioridade_atendimento"]
    })

    # Devolve a lista atualizada ao dicionário e grava tudo no disco
    dados["historico_interacoes"] = historico
    salvar_dados(ARQUIVO_JSON, dados)


## Exibe as respostas do assistente que já foram salvas no arquivo JSON
def exibir_historico():
    dados = carregar_dados(ARQUIVO_JSON)
    historico = dados.get("historico_interacoes", [])

    if len(historico) == 0:
        print("Nenhuma resposta do assistente foi salva ainda.")
        return

    print(f"\n===== HISTÓRICO DE RESPOSTAS ({len(historico)}) =====")
    # O start=1 começa a numeração em 1
    for i, interacao in enumerate(historico, start=1):
        print(f"\n{i} - [{interacao['data']}] Módulo: {interacao['modulo']}")
        print(f"    Técnica: {interacao['tecnica']}")
        print(f"    Classificação: {interacao['classificacao']} (prioridade {interacao['prioridade_atendimento']})")
        print(f"    Justificativa: {interacao['justificativa']}")
        print(f"    Ação recomendada: {interacao['acao_recomendada']}")


## Exibe o prompt escolhido pelo usuário e a resposta simulada correspondente
def simular_assistente():
    nome = input("Digite o nome do módulo: ")

    # Busca o dicionário completo do módulo pelo nome digitado
    modulos = carregar_modulos(ARQUIVO_JSON)
    modulo = None
    for m in modulos:
        # .lower() nos dois lados torna a comparação insensível a maiúsculas
        if m["nome"].lower() == nome.lower():
            modulo = m
            break   # para a busca assim que encontra

    # Se continuar None, é porque nenhum módulo com esse nome existe na colônia
    if modulo is None:
        print("Módulo não encontrado! Os módulos são: Habitat Alpha, MedBase, Reator Solar, BioLab, LogiStore e TerraBot.")
        return

    # Submenu com os três estilos de prompt disponíveis
    print("\n1 - Zero-shot")
    print("2 - Few-shot")
    print("3 - Saída estruturada (JSON)")
    escolha = input("Escolha o estilo de prompt: ")

    # Monta o prompt conforme a escolha; input() devolve texto, por isso as aspas
    if escolha == "1":
        prompt = prompt_zero_shot(modulo)
        tecnica = "Zero-shot"
    elif escolha == "2":
        prompt = prompt_few_shot(modulo)
        tecnica = "Few-shot"
    elif escolha == "3":
        prompt = prompt_structured(modulo)
        tecnica = "Saída estruturada (JSON)"
    else:
        # Sem essa verificação, qualquer tecla digitada cairia no prompt estruturado
        print("Estilo inválido! Escolha 1, 2 ou 3.")
        return

    # Exibir o prompt demonstra a estrutura da engenharia de prompts
    print("\n===== PROMPT ENVIADO =====")
    print(prompt)

    # A escolha é repassada para a resposta sair no formato que o prompt pediu
    print("===== RESPOSTA SIMULADA =====")
    print(resposta_simulada(modulo, escolha))

    # Salva a resposta no JSON para que ela continue disponível na próxima execução
    salvar_interacao(modulo, tecnica)
    print("\nResposta salva no histórico do arquivo dados_colonia.json.")


####################################################################
# 7. MENU DE NAVEGAÇÃO
####################################################################

def menu():
    # Loop infinito: só termina quando o usuário escolhe a opção 0
    while True:
        print("\n========================================")
        print("       NCAS - AURORA SIGER")
        print("========================================")
        print("1 - Cadastrar registro")
        print("2 - Consultar registros")
        print("3 - Consultar módulos")
        print("4 - Apagar registro")
        print("5 - Limpar todos os registros")
        print("6 - Analisar alertas dos módulos")
        print("7 - Simular assistente inteligente")
        print("8 - Histórico de respostas do assistente")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_registro()

        elif opcao == "2":
            registros = ler_registros(ARQUIVO_TXT)
            # strip() remove a quebra de linha para não gerar espaços duplos
            for registro in registros:
                print(registro.strip())

        elif opcao == "3":
            modulos = carregar_modulos(ARQUIVO_JSON)
            # Exibe os campos principais de cada módulo da colônia
            for modulo in modulos:
                print(f"\nNome: {modulo['nome']}")
                print(f"Tipo: {modulo['tipo']}")
                print(f"Status: {modulo['status']}")
                print(f"Risco: {modulo['nivel_risco']}")

        elif opcao == "4":
            apagar_registro(ARQUIVO_TXT)

        elif opcao == "5":
            limpar_registros(ARQUIVO_TXT)

        elif opcao == "6":
            analisar_alertas()

        elif opcao == "7":
            simular_assistente()

        elif opcao == "8":
            exibir_historico()

        elif opcao == "0":
            print("Encerrando o sistema...")
            break

        else:
            print("Opção inválida!")


# Só executa o menu quando o arquivo é rodado diretamente, não quando importado
if __name__ == "__main__":
    menu()