# coding: utf-8
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

# --- Configuração ---
BASE_URL = "https://site-festival.vercel.app"
LOGIN_URL = f"{BASE_URL}/Login"
GERENCIAMENTO_URL = f"{BASE_URL}/Gerenciamento"
ELEMENT_TIMEOUT = 10000
HEADLESS_MODE = False
# --------------------

def selecionar_autocomplete(page, label_text, opcao_index=0):
    # Clica no campo de Autocomplete baseado no label
    input_locator = page.locator(f"label:has-text('{label_text}')").locator("..").locator("input")
    input_locator.click()
    
    # Espera pela lista de opções e seleciona a opção pelo índice
    page.locator("ul[role='listbox'] li").nth(opcao_index).click()


def login(page):
    print("🔐 Realizando login...")
    page.goto(LOGIN_URL)
    page.fill('input[name="email"]', "ricardo.bavaresco.com")
    page.fill('input[name="senha"]', "admin")
    
    page.click('button[type="submit"]')
    try:
        page.wait_for_url(GERENCIAMENTO_URL, timeout=ELEMENT_TIMEOUT)
        print("✅ Login bem-sucedido.")
    except PlaywrightTimeoutError:
        print("❌ Falha no login ou redirecionamento.")
        return False
    return True

def navegar_para_historico_notas(page):
    print("📋 Navegando para 'Histórico de notas'...")
    try:
        page.click("text=Gerenciamento")
        page.click("text=Histórico de notas")
        page.wait_for_selector("text=Histórico das ultimas notas lançadas", timeout=ELEMENT_TIMEOUT)
        print("✅ Página de notas carregada.")
        return True
    except Exception as e:
        print(f"❌ Erro ao acessar histórico de notas: {e}")
        return False

def atribuir_nota(page):
    print("📝 Iniciando atribuição de nota...")
    try:
        page.click("button:has-text('Nota')")
        page.wait_for_selector("form.modal-content", timeout=ELEMENT_TIMEOUT)

        print("🔽 Selecionando campos de Autocomplete...")
        selecionar_autocomplete(page, "Categoria")
        selecionar_autocomplete(page, "Jurado")
        selecionar_autocomplete(page, "Apresentação")

        print("✏️ Preenchendo notas...")
        page.fill("input[name='notaAfinacao']", "8.5")
        page.fill("input[name='notaDiccao']", "9.0")
        page.fill("input[name='notaRitmo']", "8.0")
        page.fill("input[name='notaInterpretacao']", "9.5")

        print("📤 Submetendo nota...")
        page.click("button:has-text('Atribuir Nota')")
        page.wait_for_timeout(2000)
        print("✅ Nota atribuída com sucesso.")

    except Exception as e:
        print(f"❌ Erro durante atribuição de nota: {e}")


    except Exception as e:
        print(f"❌ Erro durante atribuição de nota: {e}")
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE, slow_mo=250)
        context = browser.new_context()
        page = context.new_page()

        try:
            if not login(page):
                return
            if not navegar_para_historico_notas(page):
                return
            atribuir_nota(page)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
