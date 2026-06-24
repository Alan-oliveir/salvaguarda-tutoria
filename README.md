# App Salvaguarda Tutoria — Plataforma de Gestão de Tutorias 🎓

O **App Salvaguarda Tutoria** é uma plataforma web desenvolvida para otimizar e acompanhar o relacionamento entre tutores voluntários e estudantes (tutorados) do programa Salvaguarda. O sistema automatiza agendamentos de reuniões e a comunicação ativa entre os participantes.

---

## 🚀 Status do Projeto & Funcionalidades Concluídas

O núcleo do ecossistema de autenticação, gestão de dados e agendamento inteligente segue padrões profissionais de mercado:

### 🔒 Autenticação & Segurança (Módulo de Usuários)
- **Acesso Customizado:** Diferenciação completa de painéis e fluxos de navegação baseado no perfil do usuário (`ADMIN`, `TUTOR` ou `TUTORADO`).
- **Segurança de Credenciais:** Fluxo robusto de redefinição e alteração de senhas internas criptografadas com tokens nativos do Django.
- **Self-Service de Acesso:** Sistema de recuperação para senhas esquecidas com envio automático de e-mails em HTML via servidor SMTP do Gmail.
- **Variáveis de Ambiente:** Blindagem total de chaves secretas e tokens através de isolamento completo em arquivo `.env`.

### 📅 Agenda & Validação Avançada (Módulo de Tutorias)
- **Controle Dinâmico de Blocos:** Tutores gerenciam seus horários recorrentes de disponibilidade semanal.
- **Calendário Interativo:** Interface assíncrona integrada ao FullCalendar onde o tutorado visualiza slots livres e realiza agendamentos diretos.
- **Prevenção de Conflitos (DRY):** Engine centralizada que impede de forma matemática marcações retroativas (no passado), sobreposições (duas reuniões no mesmo horário) ou agendamentos fora do expediente do tutor.
- **Histórico:** Controle de presenças, pautas tratadas, duração de chamadas e controle de status (`CONFIRMADA`, `REALIZADA`, `CANCELADA`).

### 📧 Notificações Inteligentes por E-mail
- **Templates Responsivos:** Disparo de e-mails dinâmicos formatados em HTML com a paleta visual da aplicação.
- **Comunicação Proativa:** Alertas automáticos para novos agendamentos e cancelamentos de reuniões para ambas as partes.
- **Entrega de Salas Virtuais:** Fluxo automático ou por acionamento manual que envia links do Google Meet diretamente para a caixa de entrada do estudante.

---

## 🛠️ Tecnologias Utilizadas

- **Core Backend:** Python 3.14+ & Django 6.0+
- **Frontend / Interface:** Django Templates, HTML5, CSS3 Customizado (BEM/Variables) e Lucide Icons.
- **Integrações de Script:** JavaScript Vanila (Modulação DOM, manipulação assíncrona e APIs Clipboard).
- **Widgets de Terceiros:** FullCalendar API & Toastify.js (Pop-ups de contexto).
- **Banco de Dados:** SQLite (Fase de desenvolvimento).

---

## 📁 Arquitetura do Projeto

A aplicação foi projetada seguindo as melhores práticas do padrão **MVT (Model-View-Template)** e modularizada internamente utilizando o princípio de *Separation of Concerns* (Separação de Conceitos):

```text
salvaguarda-project/
│
├── core/                   # Configurações globais do projeto (settings.py, urls.py)
│
├── usuarios/               # App responsável pela autenticação, perfis e ACLs
│
├── tutorias/               # App de regras de negócio educacionais
│   ├── views/              # Modularização interna (Views convertidas em Pacote)
│   │   ├── __init__.py
│   │   ├── tutorados.py    # Gestão de vínculos e prontuários
│   │   ├── disponibilidade.py # Lógica de slots e calendário
│   │   └── reunioes.py     # Fluxos de agendamentos e chamadas
│   ├── decorators.py       # Travas de segurança de acesso por tipo de conta
│   ├── emails.py           # Serviço isolado de despacho SMTP em HTML
│   ├── utils.py            # Validador de concorrência horária (Princípio DRY)
│   └── models.py           # Modelagem de banco de dados (Reuniao e Disponibilidade)
│
└── static/                 # Arquivos globais de asset unificados (CSS, JS, Imagens)
```

## 🗺️ Roadmap de Evolução

As próximas etapas mapeadas de desenvolvimento contemplam os seguintes módulos e funcionalidades:

- [ ] **Módulo de Tarefas / Exercícios:** Sistema para o tutor delegar metas semanais e o estudante acompanhar sua conclusão pelo painel.
- [ ] **Módulo de Materiais:** Repositório compartilhado para upload de PDFs, apostilas e links de estudo.
- [ ] **Módulo de Relatórios e Carga Horária:** Dashboard com exportação de relatórios e cômputo de horas de tutoria mensais.
- [ ] **Avisos Automáticos por Fila (Cron/Celery):** Lembretes de reuniões agendadas disparados automaticamente 24 horas antes do evento.

---

## 🔧 Instalação e Execução Local

### Pré-requisitos

- Python 3.14+
- Git

### Passo a passo

**1. Clone o repositório:**

```bash
git clone https://github.com/Alan-oliveir/salvaguarda-tutoria.git
cd salvaguarda-project
```

**2. Crie e ative o ambiente virtual:**

```bash
python -m venv .venv

# No Windows:
.venv\Scripts\activate

# No Linux/Mac:
source .venv/bin/activate
```

**3. Instale as dependências:**

```bash
pip install django django-environ
```

**4. Configure as variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SECRET_KEY=seu-token-django
DEBUG=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-aplicativo-de-16-digitos
```

> ⚠️ A senha de aplicativo do Gmail pode ser gerada em **Conta Google → Segurança → Senhas de app**.

**5. Aplique as migrações e colete os arquivos estáticos:**

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

**6. Inicie o servidor de desenvolvimento:**

```bash
python manage.py runserver
```

Acesse a aplicação em `http://127.0.0.1:8000`.
