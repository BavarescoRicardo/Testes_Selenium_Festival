# coding: utf-8
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
from typing import Dict, List
import json

# --- Configuração ---
BASE_URL = "https://site-festival.vercel.app"
LOGIN_URL = f"{BASE_URL}/Login"
GERENCIAMENTO_URL = f"{BASE_URL}/Gerenciamento"
ELEMENT_TIMEOUT = 15000  # Aumentado para 15 segundos
HEADLESS_MODE = False
SLOW_MO = 500  # Aumentado para melhor visualização
# --------------------

class TesteNotas:
    def __init__(self):
        self.dados_coletados: Dict[str, List[Dict]] = {}
        self.erros: List[str] = []

    def login(self, page) -> bool:
        print("🔐 Realizando login...")
        try:
            page.goto(LOGIN_URL)
            page.fill('input[name="email"]', "ricardo.bavaresco.com")
            page.fill('input[name="senha"]', "admin")
            
            page.click('button[type="submit"]')
            page.wait_for_url(GERENCIAMENTO_URL, timeout=ELEMENT_TIMEOUT)
            print("✅ Login bem-sucedido.")
            return True
        except Exception as e:
            print(f"❌ Falha no login: {str(e)}")
            return False

    def navegar_para_historico_notas(self, page) -> bool:
        print("📋 Navegando para 'Histórico de notas'...")
        try:
            page.click("text=Gerenciamento")
            page.click("text=Histórico de notas")
            page.wait_for_selector("text=Histórico das ultimas notas lançadas", timeout=ELEMENT_TIMEOUT)
            print("✅ Página de notas carregada.")
            return True
        except Exception as e:
            print(f"❌ Erro ao acessar histórico de notas: {str(e)}")
            return False

    def coletar_opcoes_disponiveis(self, page) -> Dict:
        """Coleta opções dos dropdowns com tratamento robusto"""
        print("🔄 Coletando opções disponíveis...")
        options = {
            "categorias": [],
            "jurados": [],
            "apresentacoes": []
        }
        
        try:
            # Abrir modal de nova nota
            print("  Abrindo modal de nova nota...")
            page.get_by_role("button", name="Nota", exact=True).click(timeout=1000)
            page.wait_for_selector(".modal-content", state="visible", timeout=1000)
            print("  Modal aberto")
            
            # Coletar categorias
            print("  Coletando categorias...")
            page.locator("label:has-text('Categoria') + div").click(timeout=10000)
            page.wait_for_selector("ul[role='listbox']", state="visible", timeout=10000)
            options["categorias"] = [
                item.text_content().strip() 
                for item in page.locator("ul[role='listbox'] li").all()
            ]
            page.keyboard.press("Escape")
            print(f"  Categorias coletadas: {len(options['categorias'])}")

            # Coletar jurados
            print("  Coletando jurados...")
            page.locator("label:has-text('Jurado') + div").click(timeout=10000)
            page.wait_for_selector("ul[role='listbox']", state="visible", timeout=10000)
            options["jurados"] = [
                item.text_content().strip() 
                for item in page.locator("ul[role='listbox'] li").all()
            ]
            page.keyboard.press("Escape")
            print(f"  Jurados coletadas: {len(options['jurados'])}")

            # Coletar apresentações
            print("  Coletando apresentações...")
            if options["categorias"]:
                # Selecionar primeira categoria para carregar apresentações
                page.locator("label:has-text('Categoria') + div").click(timeout=10000)
                page.locator("ul[role='listbox'] li").first.click()
                
                # Esperar carregamento das apresentações
                page.wait_for_selector("label:has-text('Apresentação') + div:not([aria-disabled])", 
                                      state="attached", timeout=15000)
                print("  Apresentações carregadas")
                
                # Coletar apresentações
                page.locator("label:has-text('Apresentação') + div").click(timeout=10000)
                page.wait_for_selector("ul[role='listbox']", state="visible", timeout=15000)
                options["apresentacoes"] = [
                    item.text_content().strip() 
                    for item in page.locator("ul[role='listbox'] li").all()
                ]
                page.keyboard.press("Escape")
                print(f"  Apresentações coletadas: {len(options['apresentacoes'])}")
            
            print("✅ Coleta de opções concluída")
            
        except Exception as e:
            print(f"⚠️ Erro na coleta: {e}")
            # page.screenshot(path="erro_coleta.png")
        finally:
            # FECHAR O MODAL DE FORMA ROBUSTA
            print("🔒 Tentando fechar o modal...")
            try:
                # Método 1: Botão Cancelar
                cancel_button = page.get_by_role("button", name="Cancelar")
                if cancel_button.is_visible(timeout=5000):
                    cancel_button.click(timeout=5000)
                    print("✅ Modal fechado com botão Cancelar")
                else:
                    # Método 2: Tecla ESC
                    page.keyboard.press("Escape")
                    print("✅ Modal fechado com ESC")
            except:
                # Método 3: Clicar fora do modal
                try:
                    page.mouse.click(10, 10)
                    print("✅ Modal fechado clicando fora")
                except:
                    print("⚠️ Não foi possível fechar o modal, continuando")
            
            # Verificação final
            try:
                page.wait_for_selector(".modal-content", state="hidden", timeout=3000)
            except:
                print("⚠️ Ainda parece haver um modal aberto, continuando com cautela")
        
        return options

    def selecionar_autocomplete(self, page, label_text: str, opcao_index: int = 0) -> str:
        """Seleciona opção em Autocomplete considerando estrutura MUI"""
        try:
            print(f"🔘 Selecionando '{label_text}'...")
            
            # Localizar o container do Autocomplete
            container = page.locator(f"label:has-text('{label_text}') + div")
            
            # Verificar se o elemento está visível e habilitado
            if not container.is_visible():
                container.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                
            container.click(timeout=10000)
            
            # Esperar o dropdown aparecer
            page.wait_for_selector("ul[role='listbox']", state="visible", timeout=10000)
            
            # Localizar todas as opções
            options = page.locator("ul[role='listbox'] li")
            count = options.count()
            
            if count == 0:
                # Tentar abrir novamente se não encontrou opções
                container.click()
                page.wait_for_selector("ul[role='listbox']", state="visible", timeout=5000)
                count = options.count()
                if count == 0:
                    raise Exception("Nenhuma opção encontrada após segunda tentativa")
            
            # Ajustar índice se necessário
            if opcao_index >= count:
                opcao_index = count - 1
                print(f"⚠️ Índice ajustado para {opcao_index} (total: {count})")
            
            # Obter texto da opção
            option_text = options.nth(opcao_index).text_content()
            
            # Foco na opção
            for _ in range(opcao_index + 1):
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(100)
            
            # Selecionar com Enter
            page.keyboard.press("Enter")
            
            # Esperar seleção ser aplicada
            page.wait_for_timeout(500)
            
            # Verificar se o valor foi selecionado
            input_value = container.locator("input").input_value()
            if not input_value:
                raise Exception(f"Valor não foi selecionado: {option_text}")
            
            print(f"✅ Selecionado: {option_text.strip()}")
            return option_text.strip()
            
        except Exception as e:
            self.erros.append(f"Erro ao selecionar '{label_text}': {str(e)}")
            # page.screenshot(path=f"erro_selecao_{label_text}.png")
            raise

    def atribuir_nota(self, page, categoria_idx: int, jurado_idx: int, apresentacao_idx: int) -> Dict:
        """Atribui nota com tratamento de dependências entre campos"""
        try:
            print("\n📝 Iniciando atribuição de nota...")
            
            # ABRIR MODAL COM MÚLTIPLAS TENTATIVAS
            for attempt in range(3):
                try:
                    print(f"  Tentativa {attempt+1} de abrir modal...")
                    page.get_by_role("button", name="Nota", exact=True).click(timeout=15000)
                    page.wait_for_selector("text=Nova Nota", timeout=15000)
                    print("✅ Modal de nova nota aberto")
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    print(f"⚠️ Falha ao abrir modal: {str(e)}")
                    page.wait_for_timeout(2000)
                    # Tentar fechar qualquer elemento que possa estar obstruindo
                    page.keyboard.press("Escape")
                    page.mouse.click(10, 10)
            
            # Selecionar categoria primeiro (carrega apresentações)
            print("🔽 Selecionando categoria...")
            categoria = self.selecionar_autocomplete(page, "Categoria", categoria_idx)
            
            # Esperar carregamento das apresentações
            page.wait_for_selector("label:has-text('Apresentação') + div:not([aria-disabled='true'])", 
                                  state="attached", timeout=15000)
            print("✅ Apresentações carregadas")
            
            # Selecionar jurado
            print("🔽 Selecionando jurado...")
            jurado = self.selecionar_autocomplete(page, "Jurado", jurado_idx)
            
            # Selecionar apresentação
            print("🔽 Selecionando apresentação...")
            apresentacao = self.selecionar_autocomplete(page, "Apresentação", apresentacao_idx)
            
            # Preencher notas
            print("✏️ Preenchendo notas...")
            notas = {
                "notaAfinacao": "8.5",
                "notaDiccao": "9.0",
                "notaRitmo": "8.0",
                "notaInterpretacao": "9.5"
            }
            
            for campo, valor in notas.items():
                field = page.locator(f"#{campo}")
                field.fill("")
                field.type(valor, delay=10)
                print(f"  - {campo}: {valor}")
            
            # Submeter
            print("📤 Submetendo nota...")
            submit_button = page.get_by_role("button", name="Atribuir Nota")
            submit_button.click()
            
            # Confirmar envio
            page.wait_for_selector("text=Nota atribuída com sucesso", timeout=15000)
            print("✅ Nota atribuída com sucesso.")
            
            # Fechar modal
            page.wait_for_timeout(150)
            if page.locator(".modal-content").is_visible():
                page.keyboard.press("Escape")
            
            return {
                "categoria": categoria,
                "jurado": jurado,
                "apresentacao": apresentacao,
                "notas": notas
            }
            
        except Exception as e:
            self.erros.append(f"Erro ao atribuir nota: {str(e)}")
            # page.screenshot(path="erro_atribuicao.png")
            # Tentar fechar o modal se ainda estiver aberto
            try:
                if page.locator(".modal-content").is_visible():
                    page.get_by_role("button", name="Cancelar").click()
            except:
                pass
            raise

    def verificar_nota_no_historico(self, page, dados_nota: Dict) -> bool:
        """Verifica se a nota aparece corretamente no histórico"""
        try:
            print(f"🔍 Verificando nota no histórico para {dados_nota['apresentacao']}...")
            
            # Recarregar a página para garantir que os dados estão atualizados
            page.reload()
            page.wait_for_selector("table tbody tr", timeout=ELEMENT_TIMEOUT)

            # Encontrar a linha correspondente
            rows = page.locator("table tbody tr")
            for i in range(rows.count()):
                cells = rows.nth(i).locator("td")
                if cells.nth(2).text_content().strip() == dados_nota["apresentacao"] and \
                   cells.nth(1).text_content().strip() == dados_nota["jurado"]:
                    
                    # Verificar notas
                    notas_historico = {
                        "Afinacao": cells.nth(3).text_content().strip(),
                        "Diccao": cells.nth(4).text_content().strip(),
                        "Ritmo": cells.nth(5).text_content().strip(),
                        "Interpretacao": cells.nth(6).text_content().strip()
                    }

                    # Comparar com os dados originais
                    for campo, valor in dados_nota["notas"].items():
                        campo_nome = campo.replace("nota", "")
                        try:
                            valor_historico = float(notas_historico[campo_nome])
                            if valor_historico != valor:
                                self.erros.append(
                                    f"Divergência de notas para {dados_nota['apresentacao']}: "
                                    f"{campo_nome} (histórico: {valor_historico}, esperado: {valor})"
                                )
                                return False
                        except:
                            self.erros.append(f"Erro ao converter nota para {campo_nome}")
                            return False

                    print("✅ Nota verificada com sucesso no histórico.")
                    return True

            self.erros.append(f"Nota não encontrada no histórico para {dados_nota['apresentacao']}")
            return False

        except Exception as e:
            self.erros.append(f"Erro ao verificar histórico: {str(e)}")
            return False

    def executar_testes_completos(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS_MODE, slow_mo=SLOW_MO)
            context = browser.new_context()
            page = context.new_page()

            try:
                if not self.login(page):
                    return
                
                if not self.navegar_para_historico_notas(page):
                    return

                # Coletar todas as opções disponíveis
                opcoes = self.coletar_opcoes_disponiveis(page)
                print(f"🔹 Categorias: {len(opcoes['categorias'])}")
                print(f"🔹 Jurados: {len(opcoes['jurados'])}")
                print(f"🔹 Apresentações: {len(opcoes['apresentacoes'])}")

                # Executar combinações (limitado para exemplo)
                max_testes = 2  # Reduzido para testes iniciais
                for cat_idx in range(min(max_testes, len(opcoes["categorias"]))):
                    for jur_idx in range(min(max_testes, len(opcoes["jurados"]))):
                        for apr_idx in range(min(max_testes, len(opcoes["apresentacoes"]))):
                            try:
                                print(f"\n▶️ Iniciando teste: Cat={cat_idx}, Jur={jur_idx}, Apr={apr_idx}")
                                dados_nota = self.atribuir_nota(page, cat_idx-1, jur_idx-1, apr_idx-1)
                                
                                if not self.verificar_nota_no_historico(page, dados_nota):
                                    print("❌ Falha na verificação")
                                
                            except Exception as e:
                                print(f"⚠️ Teste interrompido para combinação {cat_idx}-{jur_idx}-{apr_idx}: {str(e)}")
                                continue

                # Salvar dados para relatório
                with open("dados_notas.json", "w", encoding="utf-8") as f:
                    json.dump(self.dados_coletados, f, indent=2, ensure_ascii=False)

                # Resumo final
                print("\n📊 RESUMO DOS TESTES:")
                total_testes = sum(len(v) for v in self.dados_coletados.values())
                print(f"✅ Testes concluídos: {total_testes}")
                print(f"❌ Erros encontrados: {len(self.erros)}")
                
                if self.erros:
                    print("\n🔴 ERROS DETECTADOS:")
                    for erro in self.erros:
                        print(f"- {erro}")
                
                if not self.erros and total_testes > 0:
                    print("\n🎉 Todos os testes passaram com sucesso!")
                elif total_testes == 0:
                    print("\n⚠️ Nenhum teste foi concluído com sucesso")

            finally:
                browser.close()

if __name__ == "__main__":
    tester = TesteNotas()
    tester.executar_testes_completos()