# 🤖 Testes Automatizados - Festival Next

Este projeto contém testes automatizados desenvolvidos em **Python** utilizando **Playwright** e **Selenium**, focados no fluxo de inscrições da plataforma [Festival Next](https://github.com/BavarescoRicardo/FestivalNext) — um sistema para gerenciamento de festivais de música.

## 🧪 O que é testado?

- Preenchimento automático de formulários
- Validação de campos obrigatórios (CPF, RG, CEP, etc.)
- Navegação entre etapas do formulário
- Simulação de uploads de arquivos
- Submissão final do formulário com verificação de sucesso
- Envio do email após inscrições

## ⚙️ Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [Playwright para Python](https://playwright.dev/python/)
- [Selenium](https://www.selenium.dev/)

## 📂 Estrutura
├── test_inscricao.py # Script principal de automação
├── test_data.json # Dados fictícios para simulação
├── screenshots/ # Capturas opcionais durante execução
└── README.md

## ▶️ Como executar os testes

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/BavarescoRicardo/Testes_Selenium_Festival.git
   cd Testes_Selenium_Festival

    Instale as dependências:

pip install playwright selenium
playwright install

Inicie o servidor local (se necessário):

# Supondo que o front esteja em Next.js
npm run dev

Execute o teste:
    
    python test_inscricao.py

    💡 O script usa por padrão a URL http://localhost:3000/Inscricao, mas pode ser adaptado facilmente via variável BASE_URL no topo do script.

✅ Benefícios da automação

    ⏱️ Economia de tempo: testes manuais levavam horas, agora rodam em minutos

    🔒 Validação antes de cada deploy

    🐞 Detecção antecipada de falhas em campos críticos

    🧪 Testes repetíveis, confiáveis e fáceis de manter


🙋‍♂️ Autor

Ricardo Bavaresco
💼 LinkedIn: http://www.linkedin.com/in/bavarescoricardo
📧 Email: ricardobavaresco@gmail.com
