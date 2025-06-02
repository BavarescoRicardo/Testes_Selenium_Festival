# coding: utf-8
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import json
import os
from datetime import datetime

# --- Configuration ---
#BASE_URL = os.environ.get("TEST_URL", "https://site-festival.vercel.app")
BASE_URL = "http://localhost:3000"
FORM_PATH = "/Inscricao"
TARGET_URL = f"{BASE_URL}{FORM_PATH}"
DATA_FILE = "test_data.json"
HEADLESS_MODE = True
ADDRESS_AUTOFILL_WAIT_TIMEOUT = 15
ADDRESS_AUTOFILL_POLL_INTERVAL = 0.5
ELEMENT_TIMEOUT = 10000
# -------------------

def fill_step1(page, data, participant_index=0):
    print(f"Preenchendo Etapa 1: Cantor para {data["nome_responsavel"]}")
    try:
        # Campo 1: Nome Responsável
        nome_responsavel_selector = f"input[name=\"participante[{participant_index}].nomeResponsavel\"]"
        page.wait_for_selector(nome_responsavel_selector, state="visible", timeout=ELEMENT_TIMEOUT*2)
        page.locator(nome_responsavel_selector).fill(data["nome_responsavel"])
        print("  Campo \"Nome Responsável\" preenchido.")

        # Campo 2: Email
        email_selector = f"input[name=\"participante[{participant_index}].email\"]"
        page.wait_for_selector(email_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(email_selector).fill(data["email"])
        print("  Campo \"Email\" preenchido.")

        # Campo 3: Documento RG
        rg_selector = f"input[name=\"participante[{participant_index}].documentorg\"]"
        page.wait_for_selector(rg_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(rg_selector).fill(data["rg"])
        print("  Campo \"Documento RG\" preenchido.")

        # Campo 4: Data Nascimento
        data_nascimento_selector = f"input[name=\"participante[{participant_index}].nascimento\"]"
        page.wait_for_selector(data_nascimento_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        try:
            date_obj = datetime.strptime(data["data_nascimento"], "%d%m%Y")
            date_iso = date_obj.strftime("%Y-%m-%d")
            page.locator(data_nascimento_selector).fill(date_iso)
            print(f"  Campo \"Data de Nascimento\" preenchido com {date_iso}.")
        except ValueError as date_err:
            print(f"  ERRO: Falha ao converter data {data["data_nascimento"]} para YYYY-MM-DD. Erro: {date_err}")
            raise date_err
        except Exception as date_err:
            print(f"  ERRO inesperado ao processar data: {date_err}")
            raise date_err

        # Campo 5: Gênero
        genero_value = data["genero"].lower()
        genero_selector = f"input[name=\"participante[{participant_index}].genero\"][value=\"{genero_value}\"]"
        page.wait_for_selector(genero_selector, timeout=ELEMENT_TIMEOUT)
        page.locator(genero_selector).check()
        print(f"  Gênero \"{data["genero"]}\" selecionado.")

        # Campo: Nº Participantes
        num_participantes = data.get("num_participantes", 0)
        select_trigger_selector = f"#individuos-{participant_index}"
        page.wait_for_selector(select_trigger_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(select_trigger_selector).click()
        option_selector = f"li[role=\"option\"][data-value=\"{num_participantes}\"]"
        page.wait_for_selector(option_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(option_selector).click()
        print(f"  Nº Participantes selecionado: {num_participantes}")
        time.sleep(0.5)

        # Campo 6: Necessidade Especial
        necessidade_selector_base = f"input[name=\"participante[{participant_index}].necessidade\"]"
        if data["necessidade_especial"]:
            necessidade_value = "necessidadesim"
            necessidade_selector = f"{necessidade_selector_base}[value=\"{necessidade_value}\"]"
            page.wait_for_selector(necessidade_selector, timeout=ELEMENT_TIMEOUT)
            page.locator(necessidade_selector).check()
            print("  Necessidade Especial \"Sim\" selecionado.")

            qual_necessidade_selector = f"input[name=\"participante[{participant_index}].descrinescessidade\"]"
            page.wait_for_selector(qual_necessidade_selector, state="visible", timeout=ELEMENT_TIMEOUT)
            page.locator(qual_necessidade_selector).fill(data["qual_necessidade"])
            print("  Campo \"Qual Necessidade\" preenchido.")
        else:
            necessidade_value = "necessidadenao"
            necessidade_selector = f"{necessidade_selector_base}[value=\"{necessidade_value}\"]"
            page.wait_for_selector(necessidade_selector, timeout=ELEMENT_TIMEOUT)
            page.locator(necessidade_selector).check()
            print("  Necessidade Especial \"Não\" selecionado.")

        # Campo 7: Definir Senha
        senha_checkbox_selector = "input[name=\"definirSenha\"]"
        if page.locator(senha_checkbox_selector).is_visible(timeout=2000):
            if data.get("definir_senha"):
                page.locator(senha_checkbox_selector).check()
                print("  Checkbox \"Definir Senha\" marcado.")
            else:
                print("  Checkbox \"Definir Senha\" presente, mas não marcado.")
        else:
            print("  Checkbox \"Definir Senha\" não encontrado/visível.")

        # Campo 8: CPF
        cpf_selector = f"input[name=\"participante[{participant_index}].cpf\"]"
        page.wait_for_selector(cpf_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(cpf_selector).click()
        page.locator(cpf_selector).type(data["cpf"], delay=150)
        print("  Campo \"CPF\" preenchido.")

        # Campo 9: Pix
        pix_selector = f"input[name=\"participante[{participant_index}].pix\"]"
        page.wait_for_selector(pix_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(pix_selector).fill(data["pix"])
        print("  Campo \"Pix\" preenchido.")

        # Campo 10: Banco
        banco_selector = f"input[name=\"participante[{participant_index}].banco\"]"
        page.wait_for_selector(banco_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(banco_selector).fill(data["codigo_banco"])
        print("  Campo \"Código do Banco\" preenchido.")

        # Campo 11: Agencia
        agencia_selector = f"input[name=\"participante[{participant_index}].agencia\"]"
        page.wait_for_selector(agencia_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(agencia_selector).fill(data["agencia"])
        print("  Campo \"Agência\" preenchido.")

        # Campo 12: Conta
        conta_selector = f"input[name=\"participante[{participant_index}].conta\"]"
        page.wait_for_selector(conta_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(conta_selector).fill(data["conta"])
        print("  Campo \"Conta\" preenchido.")

        # Botão Próximo (Etapa 1)
        print("Clicando em Próximo após Etapa 1")
        proximo_button_selector = "button:has-text(\"Próximo\")"
        page.wait_for_selector(proximo_button_selector, timeout=ELEMENT_TIMEOUT)
        page.locator(proximo_button_selector).click()
        print("Botão \"Próximo\" (Etapa 1) clicado.")

        # Wait for navigation to Etapa 2: Endereço
        page.wait_for_selector("text=Endereço", timeout=15000)
        print("Navegou para a Etapa 2: Endereço.")
        time.sleep(1)

        print("Preenchimento da Etapa 1 concluído.")
        return True

    except PlaywrightTimeoutError as e:
        print(f"Timeout Error durante preenchimento da Etapa 1 para {data["nome_responsavel"]}: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado durante preenchimento da Etapa 1 para {data["nome_responsavel"]}: {e}")
        return False

def wait_for_autofill_or_fill_manually(page, selector, value, field_name):
    start_time = time.time()
    field_locator = page.locator(selector)
    
    print(f"  Aguardando auto-preenchimento ou visibilidade de: {field_name}")
    page.wait_for_selector(selector, state="visible", timeout=ELEMENT_TIMEOUT)
    
    while time.time() - start_time < ADDRESS_AUTOFILL_WAIT_TIMEOUT:
        current_value = field_locator.input_value()
        if current_value:
            print(f"  Campo \"{field_name}\" preenchido (auto-fill: ", current_value, ").")
            return True # Auto-filled
        time.sleep(ADDRESS_AUTOFILL_POLL_INTERVAL)

    print(f"  Timeout esperando auto-preenchimento para {field_name}. Preenchendo manualmente.")
    try:
        field_locator.fill(value)
        print(f"  Campo \"{field_name}\" preenchido (manualmente).")
        return True
    except Exception as fill_err:
        print(f"  ERRO ao tentar preencher manualmente {field_name}: {fill_err}")
        return False

def fill_step2(page, data):
    print(f"Preenchendo Etapa 2: Endereço para {data["endereco"]}")
    try:
        # Campo 1: endereco
        endereco_selector = "input[name=\"endereco\"]"
        page.wait_for_selector(endereco_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(endereco_selector).fill(data["endereco"])
        print("  Campo \"Endereco\" preenchido.")
        # Campo 2: telefone
        telefone_selector = "input[name=\"telefone\"]"
        page.wait_for_selector(telefone_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(telefone_selector).fill(data["telefone"])
        print("  Campo \"Telefone\" preenchido.")        
        # Campo 3: CEP
        cep_selector = "input[name=\"cep\"]"
        page.wait_for_selector(cep_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(cep_selector).click()
        page.locator(cep_selector).type(data["cep"], delay=100)
        print("  Campo \"CEP\" preenchido.")
        # Campo 3: cidade
        cidade_selector = "input[name=\"cidade\"]"
        page.wait_for_selector(cidade_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(cidade_selector).fill(data["cidade"])
        print("  Campo \"Cidade\" preenchido.")

        time.sleep(1)
        page.keyboard.press("Tab")
        print("  Pressionado Tab após cidade.")
        time.sleep(1)

        # Campo 6: Estado (UF) - MUI Select
        estado_value = data["estado"]
        estado_trigger_selector = "#estado"
        page.wait_for_selector(estado_trigger_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        print("  Selecionando Estado manualmente...")
        page.locator(estado_trigger_selector).click()
        print("  Dropdown de Estado aberto.")
        estado_option_selector = f"li[role=\"option\"][data-value=\"{estado_value}\"]"
        page.wait_for_selector(estado_option_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(estado_option_selector).click()
        print(f"  Estado \"{estado_value}\" selecionado.")
        time.sleep(0.5)

        # Botão Próximo (Etapa 2)
        print("Clicando em Próximo após Etapa 2")
        proximo_button_selector = "button:has-text(\"Próximo\")"
        page.wait_for_selector(proximo_button_selector, timeout=ELEMENT_TIMEOUT)
        page.locator(proximo_button_selector).click()
        print("Botão \"Próximo\" (Etapa 2) clicado.")        

        # Wait for navigation to Etapa 3: Música
        page.wait_for_selector("text=Música", timeout=1000)
        print("Navegou para a Etapa 3: Música.")
        time.sleep(1)

        print("Preenchimento da Etapa 2 concluído.")
        return True

    except PlaywrightTimeoutError as e:
        print(f"Timeout Error durante preenchimento da Etapa 2 para {data["endereco"]}: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado durante preenchimento da Etapa 2 para {data["endereco"]}: {e}")
        return False
    
def fill_step3(page, data):
    print(f"Preenchendo Etapa 3: Música para {data['nomeartistico']}")
    try:
        # Campo 1: nomeartistico
        nomeartistico_selector = "input[name=\"nomeartistico\"]"
        page.wait_for_selector(nomeartistico_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(nomeartistico_selector).fill(data["nomeartistico"])
        print("  Campo \"NomeArtistico\" preenchido.")
        # Campo 2: musica
        musica_selector = "input[name=\"musica\"]"
        page.wait_for_selector(musica_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(musica_selector).fill(data["musica"])
        print("  Campo \"Música\" preenchido.")        
        # Campo 3: linkmusica
        linkmusica_selector = "input[name=\"linkmusica\"]"
        page.wait_for_selector(linkmusica_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(linkmusica_selector).click()
        page.locator(linkmusica_selector).type(data["linkmusica"], delay=100)
        print("  Campo \"LinkMusica\" preenchido.")
        # Campo 4: gravacao
        gravacao_selector = "input[name=\"gravacao\"]"
        page.wait_for_selector(gravacao_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(gravacao_selector).fill(data["gravacao"])
        print("  Campo \"Gravacao\" preenchido.")

        # Campo 5: autor
        autor_selector = "input[name=\"autor\"]"
        page.wait_for_selector(autor_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(autor_selector).fill(data["autor"])
        print("  Campo \"Autor\" preenchido.")        

        time.sleep(1)
        page.keyboard.press("Tab")
        print("  Pressionado Tab após autor.")
        time.sleep(1)

        # Campo 6: categoria
        categoria_value = data["categoria"]
        categoria_input_selector = "#categoria"
        page.wait_for_selector(categoria_input_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        print("  Selecionando Categoria...")

        # Digita no campo de categoria
        # page.locator(categoria_input_selector).fill(categoria_value)        

        # Pressiona seta para baixo e enter para selecionar a sugestão
        page.keyboard.press("ArrowDown")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        print(f"  Categoria \"{categoria_value}\" selecionada.")
        time.sleep(0.5)

        # Campo 7: tom
        tom_selector = "input[name=\"tom\"]"
        page.wait_for_selector(tom_selector, state="visible", timeout=ELEMENT_TIMEOUT)
        page.locator(tom_selector).fill(data["tom"])
        print("  Campo \"Tom\" preenchido.")
        time.sleep(1)

        # Botão Próximo (Etapa 3)
        print("Clicando em Próximo após Etapa 3")
        proximo_button_selector = "button:has-text(\"Próximo\")"
        page.wait_for_selector(proximo_button_selector, timeout=ELEMENT_TIMEOUT)
        page.locator(proximo_button_selector).click()
        print("Botão \"Próximo\" (Etapa 3) clicado.")        

        # Wait for navigation to Etapa 4: Dados Finais
        page.wait_for_selector("text=Dados Finais", timeout=1000)
        print("Navegou para a Etapa 4: Dados Finais.")
        time.sleep(1)

        print("Preenchimento da Etapa 3 concluído.")
        return True

    except PlaywrightTimeoutError as e:
        print(f"Timeout Error durante preenchimento da Etapa 3 para {data['nomeartistico']}: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado durante preenchimento da Etapa 3 para {data['nomeartistico']}: {e}")
        return False    

# Load test data
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        test_data_list = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo de dados {DATA_FILE} não encontrado.")
    exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar JSON do arquivo {DATA_FILE}. Verifique o formato.")
    exit(1)

print(f"Iniciando testes em: {TARGET_URL}")
print(f"Modo Headless: {HEADLESS_MODE}")

with sync_playwright() as p:
    #browser = p.chromium.launch(headless=HEADLESS_MODE)
    browser = p.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    all_tests_passed = True
    for i, test_data in enumerate(test_data_list):
        print(f"\n--- Iniciando Teste {i+1} para {test_data["nome_responsavel"]} ---")
        step1_success = False
        step2_success = False
        try:
            print(f"Navegando para {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            print("Página carregada.")

            # Execute Step 1
            step1_success = fill_step1(page, test_data)

            # Execute Step 2 only if Step 1 succeeded
            if step1_success:
                step2_success = fill_step2(page, test_data)
            else:
                print("Etapa 1 falhou, pulando Etapa 2.")

            # Execute Step 3 only if Step 2 succeeded
            if step2_success:
                step3_success = fill_step3(page, test_data)
            else:
                print("Etapa 2 falhou, pulando Etapa 3.")                

            if step1_success and step2_success and step3_success:
                print(f"Inscrição (Etapas 1 e 2 e 3) com {test_data["nomeartistico"]} processada com sucesso.")
            else:
                 print(f"Falha no processamento da inscrição para {test_data["nome_responsavel"]}.")
                 all_tests_passed = False

        except Exception as e:
            print(f"Erro geral ao processar inscrição para {test_data["nome_responsavel"]}: {e}")
            all_tests_passed = False
        finally:
            test_passed = step1_success and step2_success and step3_success
            print(f"--- Teste {i+1} para {test_data["nome_responsavel"]} concluído (Sucesso: {test_passed}) ---")

    print(f"\nTodos os testes foram executados. Sucesso geral: {all_tests_passed}")
    browser.close()

