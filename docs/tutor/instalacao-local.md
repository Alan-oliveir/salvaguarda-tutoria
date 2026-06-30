# Instalação e Execução Local

Siga o passo a passo abaixo para rodar o ecossistema do Salvaguarda na sua máquina de desenvolvimento.

## Pré-requisitos

- **Python 3.14+** (utilizado no core do projeto)
- **Git**

## Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/Alan-oliveir/salvaguarda-tutoria.git
cd salvaguarda-project

# 2. Crie e ative o ambiente virtual (Virtualenv)
python -m venv .venv

# No Windows:
.venv\Scripts\activate

# No Linux/Mac:
source .venv/bin/activate

# 3. Instale as dependências estruturais
pip install --no-cache-dir -r requirements.txt
```

## Arquitetura de Módulos (Django MVT)

O projeto é dividido em aplicações focadas no princípio de *Separation of Concerns*:

- `usuarios/` — Controle de autenticação, criptografia, perfis (`ADMIN`, `TUTOR`, `TUTORADO`) e recuperação de senhas.
- `tutorias/` — Motor de agendamento, envio de e-mails via SMTP e validações de concorrência horária.
- `tarefas/` — Gestão de metas pedagógicas semanais.
- `materiais/` — Repositório compartilhado para upload de arquivos de estudo.

---

# Deploy em Produção (Docker)

O projeto já está completamente "Dockerizado", permitindo que você faça o deploy de forma idêntica em plataformas PaaS (como Northflank ou Render) ou em uma VPS própria (como a Oracle Cloud).

## Variáveis de Ambiente Obrigatórias

Ao configurar o container no seu provedor de nuvem, certifique-se de injetar as seguintes **Runtime Variables**:

| Variável | Descrição | Exemplo / Formato |
| :--- | :--- | :--- |
| `DEBUG` | Deve ser falso em produção por segurança | `False` |
| `SECRET_KEY` | Chave criptográfica única do Django | `uma-string-longa-e-aleatoria` |
| `DATABASE_URL` | URL de conexão PostgreSQL (ex: Neon DB) | `postgres://usuario:senha@host/banco` |
| `ALLOWED_HOSTS` | Domínios ou IPs autorizados | `seu-app.northflank.app` |
| `CSRF_TRUSTED_ORIGINS` | Origens confiáveis para requisições POST | `https://seu-app.northflank.app` |

::: warning ATENÇÃO SOBRE O CSRF
A variável `CSRF_TRUSTED_ORIGINS` obrigatoriamente exige o prefixo `https://`. Caso contrário, o Django retornará um erro *403 Forbidden* ao tentar enviar formulários ou fazer login.
:::