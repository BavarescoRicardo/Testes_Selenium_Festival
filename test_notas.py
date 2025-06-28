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
    page.fill('input[name="usuario"]', "ricardo.bavaresco.com")
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
        # Abrir modal de nova nota
        page.click("button:has-text('Nota')")
        page.wait_for_selector("text=Nova Nota", timeout=ELEMENT_TIMEOUT)

        # Selecionar categoria
        page.locator("text=Categoria").first.click()
        page.locator("ul[role='listbox'] li").nth(1).click()  # Seleciona a segunda opção (índice 1)

        # Selecionar jurado
        page.locator("text=Jurado").first.click()
        page.locator("ul[role='listbox'] li").nth(1).click()

        # Selecionar apresentação
        page.locator("text=Apresentação").first.click()
        page.locator("ul[role='listbox'] li").nth(1).click()

        # Preencher notas
        page.fill("input[aria-label='Afinação']", "8.5")
        page.fill("input[aria-label='Dicção']", "9.0")
        page.fill("input[aria-label='Ritmo']", "8.0")
        page.fill("input[aria-label='Interpretação']", "9.5")

        # Confirmar
        page.click("button:has-text('ATRIBUIR NOTA')")
        time.sleep(2)
        print("✅ Nota atribuída com sucesso.")

    except Exception as e:
        print(f"❌ Erro durante atribuição de nota: {e}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
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
