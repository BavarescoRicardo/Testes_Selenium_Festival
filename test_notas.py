# coding: utf-8
from playwright.sync_api import sync_playwright
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import csv
import random

# --- Configuração ---
BASE_URL = "https://site-festival.vercel.app"
LOGIN_URL = f"{BASE_URL}/Login"
GERENCIAMENTO_URL = f"{BASE_URL}/Gerenciamento"
ELEMENT_TIMEOUT = 15000
HEADLESS_MODE = False
SLOW_MO = 150
MAX_RETRIES = 3
# --------------------

@dataclass
class NotaAtribuida:
    categoria: str
    jurado: str
    apresentacao: str
    notas: Dict[str, float]
    timestamp: str
    status: str

class AtribuidorNotas:
    def __init__(self):
        self.resultados: List[NotaAtribuida] = []
        self.arquivo_saida = f"notas_atribuidas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._criar_arquivo()

    def _criar_arquivo(self):
        with open(self.arquivo_saida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp', 'Categoria', 'Jurado', 'Apresentacao',
                'NotaAfinacao', 'NotaDiccao', 'NotaRitmo', 'NotaInterpretacao',
                'Status'
            ])

    def _salvar_resultado(self, resultado: NotaAtribuida):
        with open(self.arquivo_saida, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                resultado.timestamp,
                resultado.categoria,
                resultado.jurado,
                resultado.apresentacao,
                resultado.notas.get('notaAfinacao', ''),
                resultado.notas.get('notaDiccao', ''),
                resultado.notas.get('notaRitmo', ''),
                resultado.notas.get('notaInterpretacao', ''),
                resultado.status
            ])

    def login(self, page) -> bool:
        print("🔐 Realizando login...")
        try:
            page.goto(LOGIN_URL, timeout=ELEMENT_TIMEOUT)
            page.fill('input[name="email"]', "ricardo.bavaresco.com")
            page.fill('input[name="senha"]', "admin")
            with page.expect_navigation(timeout=ELEMENT_TIMEOUT):
                page.click('button[type="submit"]')
            print("✅ Login bem-sucedido")
            return True
        except Exception as e:
            print(f"❌ Falha no login: {str(e)}")
            return False

    def navegar_para_historico(self, page) -> bool:
        print("📋 Acessando histórico...")
        try:
            page.click("text=Gerenciamento", timeout=ELEMENT_TIMEOUT)
            page.click("text=Histórico de notas", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("text=Histórico das ultimas notas lançadas", timeout=ELEMENT_TIMEOUT)
            print("✅ Página carregada")
            return True
        except Exception as e:
            print(f"❌ Falha ao acessar histórico: {str(e)}")
            return False

    def _abrir_modal_nota(self, page) -> bool:
        for attempt in range(MAX_RETRIES):
            try:
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                page.click("button:has-text('Nota')", timeout=5000)
                page.wait_for_selector(".modal-content", state="visible", timeout=5000)
                return True
            except Exception as e:
                print(f"⚠️ Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    return False
                page.wait_for_timeout(1000)
        return False

    def _preencher_nota(self, page, categoria: str, jurado: str, apresentacao: str) -> Dict[str, float]:
        try:
            # Selecionar categoria
            page.click("label:has-text('Categoria') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)
            page.locator(f"ul[role='listbox'] li:has-text('{categoria}')").click()
            
            # Selecionar jurado
            page.click("label:has-text('Jurado') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)
            page.locator(f"ul[role='listbox'] li:has-text('{jurado}')").click()
            
            # Esperar carregamento da API (~300ms)
            page.wait_for_timeout(500)

            # Selecionar apresentação
            page.click("label:has-text('Apresentação') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)

            apresentacao_locator = page.locator(f"ul[role='listbox'] li:has-text('{apresentacao}')")
            count = apresentacao_locator.count()
            if count == 0:
                raise Exception(f"Apresentação '{apresentacao}' não encontrada.")
            apresentacao_locator.first.click()

            # Notas aleatórias de 6.0 a 10.0 com 1 casa decimal
            notas = {
                'notaAfinacao': round(random.uniform(6.0, 10.0), 1),
                'notaDiccao': round(random.uniform(6.0, 10.0), 1),
                'notaRitmo': round(random.uniform(6.0, 10.0), 1),
                'notaInterpretacao': round(random.uniform(6.0, 10.0), 1)
            }

            for campo, valor in notas.items():
                page.fill(f"input[name='{campo}']", str(valor), timeout=ELEMENT_TIMEOUT)

            return notas
        except Exception as e:
            print(f"❌ Erro ao preencher nota: {str(e)}")
            raise


    def atribuir_nota(self, page, categoria: str, jurado: str, apresentacao: str) -> NotaAtribuida:
        resultado = NotaAtribuida(
            categoria=categoria,
            jurado=jurado,
            apresentacao=apresentacao,
            notas={},
            timestamp=datetime.now().isoformat(),
            status="Falha"
        )

        try:
            print(f"\n📝 Atribuindo nota para: {apresentacao}")
            
            if not self._abrir_modal_nota(page):
                raise Exception("Não foi possível abrir o modal de nota após várias tentativas")
            
            resultado.notas = self._preencher_nota(page, categoria, jurado, apresentacao)
            
            with page.expect_response(lambda response: "notas" in response.url and response.request.method == "POST"):
                page.click("button:has-text('Atribuir Nota')", timeout=ELEMENT_TIMEOUT)
            
            page.wait_for_selector("input[name='notaAfinacao'][value='']", timeout=5000)
            resultado.status = "Sucesso"
            print("✅ Nota atribuída com sucesso")
            
            return resultado
            
        except Exception as e:
            resultado.status = f"Erro: {str(e)}"
            print(f"❌ Falha: {str(e)}")
            return resultado
        finally:
            self._salvar_resultado(resultado)

    def executar(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS_MODE, slow_mo=SLOW_MO)
            context = browser.new_context()
            page = context.new_page()

            try:
                if not self.login(page):
                    raise Exception("Falha no login - abortando")
                
                if not self.navegar_para_historico(page):
                    raise Exception("Falha ao acessar histórico - abortando")
                
                categorias = self._coletar_opcoes(page, "Categoria")
                jurados = self._coletar_opcoes(page, "Jurado")
                
                apresentacoes_por_categoria = []
                for cat in categorias:
                    apresentacoes = self._coletar_apresentacoes_para_categoria(page, cat)
                    apresentacoes_por_categoria.append((cat, apresentacoes))
                
                for categoria, apresentacoes in apresentacoes_por_categoria:
                    for jurado in jurados:
                        for apresentacao in apresentacoes:
                            self.atribuir_nota(page, categoria, jurado, apresentacao)
                
                print("\n📊 Relatório final salvo em:", self.arquivo_saida)
                
            finally:
                browser.close()

    def _coletar_opcoes(self, page, label: str) -> List[str]:
        try:
            self._abrir_modal_nota(page)
            page.click(f"label:has-text('{label}') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)
            opcoes = [item.inner_text().strip() for item in page.locator("ul[role='listbox'] li").all()]
            page.keyboard.press("Escape")
            return opcoes
        except Exception as e:
            print(f"❌ Falha ao coletar opções de {label}: {str(e)}")
            return []

    def _coletar_apresentacoes_para_categoria(self, page, categoria: str) -> List[str]:
        try:
            self._abrir_modal_nota(page)
            page.click("label:has-text('Categoria') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)
            page.locator(f"ul[role='listbox'] li:has-text('{categoria}')").click()
            page.wait_for_timeout(500)
            page.click("label:has-text('Apresentação') + div", timeout=ELEMENT_TIMEOUT)
            page.wait_for_selector("ul[role='listbox']", timeout=ELEMENT_TIMEOUT)
            apresentacoes = [item.inner_text().strip() for item in page.locator("ul[role='listbox'] li").all()]
            page.keyboard.press("Escape")
            return apresentacoes
        except Exception as e:
            print(f"❌ Falha ao coletar apresentações para {categoria}: {str(e)}")
            return []

if __name__ == "__main__":
    atribuidor = AtribuidorNotas()
    atribuidor.executar()
