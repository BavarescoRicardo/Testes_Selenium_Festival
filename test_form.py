# coding: utf-8
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import json
import os
from datetime import datetime

# --- Configuration ---
# Default to Vercel URL, user can change this locally by setting TEST_URL environment variable
#BASE_URL = os.environ.get("TEST_URL", "https://site-festival.vercel.app")
BASE_URL = "http://localhost:3000"
FORM_PATH = "/Inscricao"
TARGET_URL = f"{BASE_URL}{FORM_PATH}"
DATA_FILE = "test_data.json"
HEADLESS_MODE = True # Set to False for local debugging with UI
# -------------------

def fill_form(page, data, participant_index=0):
    print(f"Preenchendo formulário com dados: {data["nome_responsavel"]}")

    print("Preenchendo Etapa 1: Cantor")
    try:
        # --- Using corrected name attribute selectors based on diagnostic HTML ---

        # Campo 1: Nome Responsável
        nome_responsavel_selector = f"input[name=\"participante[{participant_index}].nomeResponsavel\"]"
        print(f"Tentando localizar: {nome_responsavel_selector}")
        page.wait_for_selector(nome_responsavel_selector, state="visible", timeout=20000)
        page.locator(nome_responsavel_selector).fill(data["nome_responsavel"])
        print("Campo \"Nome Responsável\" preenchido.")

        # Campo 2: Email
        email_selector = f"input[name=\"participante[{participant_index}].email\"]"
        print(f"Tentando localizar: {email_selector}")
        page.wait_for_selector(email_selector, state="visible", timeout=10000)
        page.locator(email_selector).fill(data["email"])
        print("Campo \"Email\" preenchido.")

        # Campo 3: Documento RG (Corrected name based on HTML: documentorg)
        rg_selector = f"input[name=\"participante[{participant_index}].documentorg\"]"
        print(f"Tentando localizar: {rg_selector}")
        page.wait_for_selector(rg_selector, state="visible", timeout=10000)
        page.locator(rg_selector).fill(data["rg"])
        print("Campo \"Documento RG\" preenchido.")

        # Campo 4: Data Nascimento (Corrected name based on HTML: nascimento)
        data_nascimento_selector = f"input[name=\"participante[{participant_index}].nascimento\"]"
        print(f"Tentando localizar: {data_nascimento_selector}")
        page.wait_for_selector(data_nascimento_selector, state="visible", timeout=10000)
        # Convert date from JSON (assuming DDMMYYYY) to YYYY-MM-DD for input type=date
        try:
            date_obj = datetime.strptime(data["data_nascimento"], "%d%m%Y")
            date_iso = date_obj.strftime("%Y-%m-%d")
            page.locator(data_nascimento_selector).fill(date_iso)
            print(f"Campo \"Data de Nascimento\" preenchido com {date_iso}.")
        except ValueError as date_err:
            print(f"ERRO: Falha ao converter data {data["data_nascimento"]} para YYYY-MM-DD. Erro: {date_err}")
            raise date_err
        except Exception as date_err:
            print(f"ERRO inesperado ao processar data: {date_err}")
            raise date_err

        # Campo 5: Gênero (Corrected name based on HTML: genero, values are lowercase)
        genero_value = data["genero"].lower()
        genero_selector = f"input[name=\"participante[{participant_index}].genero\"][value=\"{genero_value}\"]"
        print(f"Tentando localizar: {genero_selector}")
        page.wait_for_selector(genero_selector, timeout=10000)
        page.locator(genero_selector).check()
        print(f"Gênero \"{data["genero"]}\" selecionado.")

        # --- Campo: Nº Participantes (MUI Select) ---
        num_participantes = data.get("num_participantes", 1) # Default to 1 if not provided
        select_trigger_selector = f"#individuos-{participant_index}"
        print(f"Tentando localizar seletor de Nº Participantes: {select_trigger_selector}")
        page.wait_for_selector(select_trigger_selector, state="visible", timeout=10000)
        page.locator(select_trigger_selector).click()
        print("Dropdown de Nº Participantes aberto.")
        option_selector = f"li[role=\"option\"][data-value=\"{num_participantes}\"]"
        print(f"Tentando localizar opção: {option_selector}")
        page.wait_for_selector(option_selector, state="visible", timeout=10000)
        page.locator(option_selector).click()
        print(f"Nº Participantes selecionado: {num_participantes}")
        time.sleep(0.5)
        # --- End Nº Participantes ---

        # Campo 6: Necessidade Especial (Corrected name: necessidade, values: necessidadesim/necessidadenao)
        necessidade_selector_base = f"input[name=\"participante[{participant_index}].necessidade\"]"
        if data["necessidade_especial"]:
            necessidade_value = "necessidadesim"
            necessidade_selector = f"{necessidade_selector_base}[value=\"{necessidade_value}\"]"
            print(f"Tentando localizar: {necessidade_selector}")
            page.wait_for_selector(necessidade_selector, timeout=10000)
            page.locator(necessidade_selector).check()
            print("Necessidade Especial \"Sim\" selecionado.")

            qual_necessidade_selector = f"input[name=\"participante[{participant_index}].descrinescessidade\"]"
            print(f"Tentando localizar: {qual_necessidade_selector}")
            page.wait_for_selector(qual_necessidade_selector, state="visible", timeout=10000)
            page.locator(qual_necessidade_selector).fill(data["qual_necessidade"])
            print("Campo \"Qual Necessidade\" preenchido.")
        else:
            necessidade_value = "necessidadenao"
            necessidade_selector = f"{necessidade_selector_base}[value=\"{necessidade_value}\"]"
            print(f"Tentando localizar: {necessidade_selector}")
            page.wait_for_selector(necessidade_selector, timeout=10000)
            page.locator(necessidade_selector).check()
            print("Necessidade Especial \"Não\" selecionado.")

        # Campo 7: Definir Senha (Check if present before interacting)
        senha_checkbox_selector = "input[name=\"definirSenha\"]"
        print(f"Verificando presença do campo: {senha_checkbox_selector}")
        if page.locator(senha_checkbox_selector).is_visible(timeout=2000):
            if data.get("definir_senha"):
                print(f"Tentando marcar: {senha_checkbox_selector}")
                page.locator(senha_checkbox_selector).check()
                print("Checkbox \"Definir Senha\" marcado.")
            else:
                print("Checkbox \"Definir Senha\" presente, mas não marcado conforme dados.")
        else:
            print("Checkbox \"Definir Senha\" não encontrado/visível.")

        # Campo 8: CPF (Corrected name based on HTML: cpf)
        cpf_selector = f"input[name=\"participante[{participant_index}].cpf\"]"
        print(f"Tentando localizar: {cpf_selector}")
        page.wait_for_selector(cpf_selector, state="visible", timeout=10000)
        page.locator(cpf_selector).click()
        page.locator(cpf_selector).type(data["cpf"], delay=150)
        print("Campo \"CPF\" preenchido.")

        # Campo 9: Pix (Corrected name based on HTML: pix)
        pix_selector = f"input[name=\"participante[{participant_index}].pix\"]"
        print(f"Tentando localizar: {pix_selector}")
        page.wait_for_selector(pix_selector, state="visible", timeout=10000)
        page.locator(pix_selector).fill(data["pix"])
        print("Campo \"Pix\" preenchido.")

        # Campo 10: Banco (Corrected name based on HTML: banco)
        banco_selector = f"input[name=\"participante[{participant_index}].banco\"]"
        print(f"Tentando localizar: {banco_selector}")
        page.wait_for_selector(banco_selector, state="visible", timeout=10000)
        page.locator(banco_selector).fill(data["codigo_banco"])
        print("Campo \"Código do Banco\" preenchido.")

        # Campo 11: Agencia (Corrected name based on HTML: agencia)
        agencia_selector = f"input[name=\"participante[{participant_index}].agencia\"]"
        print(f"Tentando localizar: {agencia_selector}")
        page.wait_for_selector(agencia_selector, state="visible", timeout=10000)
        page.locator(agencia_selector).fill(data["agencia"])
        print("Campo \"Agência\" preenchido.")

        # Campo 12: Conta (Corrected name based on HTML: conta)
        conta_selector = f"input[name=\"participante[{participant_index}].conta\"]"
        print(f"Tentando localizar: {conta_selector}")
        page.wait_for_selector(conta_selector, state="visible", timeout=10000)
        page.locator(conta_selector).fill(data["conta"])
        print("Campo \"Conta\" preenchido.")

        # Botão Próximo
        print("Clicando em Próximo após Etapa 1")
        proximo_button_selector = "button:has-text(\"Próximo\")"
        page.wait_for_selector(proximo_button_selector, timeout=10000)
        page.locator(proximo_button_selector).click()
        print("Botão \"Próximo\" clicado.")

        # Wait for navigation to Etapa 2: Endereço
        page.wait_for_selector("text=Endereço", timeout=15000)
        print("Navegou para a Etapa 2: Endereço.")
        time.sleep(1)

        print("Preenchimento da Etapa 1 e clique em Próximo concluídos. Próximas etapas não implementadas.")
        # REMOVED: Screenshot on success
        # screenshot_path = f"success_step1_{data["nome_responsavel"].replace(" ", "_")}.png"
        # page.screenshot(path=screenshot_path)
        # print(f"Screenshot da Etapa 1 salva em: {screenshot_path}")

    except PlaywrightTimeoutError as e:
        print(f"Timeout Error durante preenchimento para {data["nome_responsavel"]}: {e}")
        # REMOVED: HTML saving on timeout
        save_debug_html(page, f"{debug_prefix}_on_timeout")
        raise
    except Exception as e:
        print(f"Erro inesperado durante preenchimento para {data["nome_responsavel"]}: {e}")
        # REMOVED: HTML saving on exception
        save_debug_html(page, f"{debug_prefix}_on_exception")
        raise

# Function to save debug HTML
def save_debug_html(page, filename_prefix):
    try:
        print(f"--- Salvando HTML para depuração ({filename_prefix}) ---")
        form_locator = page.locator("form").first
        form_html = form_locator.inner_html(timeout=5000)
        filepath = f"{filename_prefix}.html"
        with open(filepath, "w", encoding="utf-8") as f_html:
            f_html.write(form_html)
        print(f"HTML do formulário salvo em: {filepath}")
    except Exception as html_error:
        print(f"Não foi possível obter/salvar o HTML do formulário: {html_error}")
        try:
            body_html = page.locator("body").inner_html(timeout=5000)
            filepath = f"{filename_prefix}_body.html"
            with open(filepath, "w", encoding="utf-8") as f_html:
                f_html.write(body_html)
            print(f"HTML do body salvo em: {filepath}")
        except Exception as body_html_error:
            print(f"Não foi possível obter/salvar o HTML do body: {body_html_error}")
    print("--- Fim da depuração de HTML ---")

# Load test data
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        test_data_list = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo de dados ", DATA_FILE, " não encontrado.")
    exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar JSON do arquivo ", DATA_FILE, ". Verifique o formato.")
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
        test_passed = False
        try:
            print(f"Navegando para {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            print("Página carregada.")

            fill_form(page, test_data)
            print(f"Inscrição (Etapa 1) com {test_data["nome_responsavel"]} processada com sucesso.")
            test_passed = True

        except Exception as e:
            print(f"Erro ao processar inscrição para {test_data["nome_responsavel"]}: {e}")
            all_tests_passed = False
            # REMOVED: Screenshot on error
            # screenshot_path = f"error_{test_data["nome_responsavel"].replace(" ", "_")}_{int(time.time())}.png"
            # try:
            #     page.screenshot(path=screenshot_path)
            #     print(f"Screenshot de erro salvo em: {screenshot_path}")
            # except Exception as screenshot_error:
            #     print(f"Falha ao salvar screenshot de erro: {screenshot_error}")
        finally:
            print(f"--- Teste {i+1} para {test_data["nome_responsavel"]} concluído (Sucesso: {test_passed}) ---")

    print(f"\nTodos os testes foram executados. Sucesso geral: {all_tests_passed}")
    browser.close()

