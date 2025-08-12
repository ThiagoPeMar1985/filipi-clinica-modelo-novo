# Sistema PDV - Quiosque Aquarius

Sistema de Ponto de Venda (PDV) desenvolvido para bares e restaurantes, com interface amigável e módulos integrados para gestão de mesas, delivery, cadastros e financeiro.

## 🚀 Como executar o projeto

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone o repositório:
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd Quiosque-Aquarius
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Execute a aplicação:
   ```bash
   python main.py
   ```

## 🏗️ Estrutura do Projeto

```
Quiosque-Aquarius/
├── src/
│   ├── config/           # Configurações e estilos
│   ├── controllers/      # Lógica de controle
│   ├── models/           # Modelos de dados
│   └── views/            # Interface do usuário
│       ├── componentes/   # Componentes reutilizáveis
│       └── telas/         # Telas da aplicação
├── main.py               # Ponto de entrada
└── README.md
```

## 🛠️ Módulos Principais

- **Cadastro**: Gestão de clientes, produtos, categorias e funcionários
- **Mesas**: Controle de comandas e mesas do estabelecimento
- **Delivery**: Gestão de pedidos para entrega
- **Financeiro**: Controle de caixa e relatórios financeiros
- **Configurações**: Personalização do sistema e gerenciamento de usuários
- **Chat**: Chat em tempo real entre usuários

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- [Seu Nome] - Desenvolvedor Principal

## 🙏 Agradecimentos

- À equipe de desenvolvimento por tornar este projeto possível
- Aos testadores por suas valiosas contribuições e feedback
