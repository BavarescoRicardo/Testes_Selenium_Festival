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
    page.wait_for_timeout(3000)
    print("📝 Iniciando atribuição de nota...")
    try:
        # Abrir modal
        page.click("button:has-text('Nota')")

        # Esperar pela modal da nota ficar visível
        modal = page.locator("form.modal-content")
        modal.wait_for(state="visible", timeout=ELEMENT_TIMEOUT)

        print("🔽 Selecionando dropdowns...")

        # Selecionar opções nos três selects
        modal.locator("select").nth(0).select_option(index=1)  # Categoria (segunda opção)
        modal.locator("select").nth(1).select_option(index=1)  # Jurado
        modal.locator("select").nth(2).select_option(index=1)  # Apresentação

        print("✏️ Preenchendo notas...")
        # Preencher os campos numéricos
        modal.locator("input[name='notaAfinacao']").fill("8.5")
        modal.locator("input[name='notaDiccao']").fill("9.0")
        modal.locator("input[name='notaRitmo']").fill("8.0")
        modal.locator("input[name='notaInterpretacao']").fill("9.5")

        print("📤 Submetendo nota...")
        modal.locator("button:has-text('ATRIBUIR NOTA')").click()

        # Tempo para o envio ser processado
        page.wait_for_timeout(2000)
        print("✅ Nota atribuída com sucesso.")

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
