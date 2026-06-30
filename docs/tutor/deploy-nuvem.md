# Deploy em Produção

O projeto Salvaguarda foi estruturado com foco em portabilidade. A presença de um `Dockerfile` na raiz do repositório garante que a aplicação possa ser provisionada de forma padronizada em diferentes provedores de nuvem, eliminando inconsistências entre o ambiente de desenvolvimento e produção.

Existem duas estratégias principais para publicar a aplicação: **PaaS** (Plataforma como Serviço) e **VPS** (Servidor Virtual Privado).

## Variáveis de Ambiente Essenciais

Independentemente da infraestrutura escolhida, você deverá injetar as seguintes variáveis de ambiente (*Environment Variables* ou *Runtime Secrets*) no painel do seu provedor para que o container inicie corretamente:

| Variável | Descrição | Exemplo de Valor |
| :--- | :--- | :--- |
| `DEBUG` | Define o modo de execução. Deve ser desativado em produção. | `False` |
| `SECRET_KEY` | Chave criptográfica única de segurança do Django. | `sua-chave-longa-e-segura` |
| `DATABASE_URL` | String de conexão para o PostgreSQL (ex: Neon, Supabase). | `postgres://usuario:senha@host/banco` |
| `ALLOWED_HOSTS` | Domínio público gerado pelo seu provedor. | `seu-app.provedor.com` |
| `CSRF_TRUSTED_ORIGINS` | Origens validadas para submissão de formulários. | `https://seu-app.provedor.com` |

::: warning Atenção Crítica de Segurança
A variável `CSRF_TRUSTED_ORIGINS` exige a declaração explícita do protocolo `https://`. A ausência deste prefixo resultará na interrupção da aplicação com um erro *403 Forbidden* durante tentativas de autenticação ou envio de formulários.
:::

## Estratégia 1: Plataformas PaaS (Northflank, Render, Railway)

As plataformas PaaS gerenciam a infraestrutura subjacente automaticamente. São ideais para implementações rápidas, pois abstraem a configuração do sistema operacional.

### Fluxo de Implantação:

1. **Conexão com o Repositório:** Crie um novo serviço web na plataforma escolhida e vincule o seu repositório do GitHub.
2. **Método de Build:** Selecione a opção para utilizar o `Dockerfile` (evite os *Buildpacks* nativos, pois o Dockerfile do repositório já contém as otimizações do sistema operacionais necessárias para o Django).
3. **Injeção de Variáveis:** Acesse a aba de *Environment Variables* ou *Secrets* do painel da plataforma e adicione todas as chaves listadas na tabela superior.
4. **Mapeamento de Portas:** Caso a plataforma solicite o redirecionamento de rede (Networking/Ports), certifique-se de expor a porta **8000** via protocolo **HTTP**. O container foi configurado para responder o servidor Gunicorn nesta porta.

::: tip Recomendação de Recursos
O ecossistema Django requer processamento para compilação de pacotes e memória para gerenciar múltiplos acessos simultâneos (Workers do Gunicorn). Recomenda-se selecionar um plano que ofereça, no mínimo, **512 MB de RAM** para evitar falhas por falta de memória (*OOMKilled*) durante a etapa de build.
:::

## Estratégia 2: Servidores Virtuais - VPS (Oracle Cloud, AWS EC2)

A utilização de uma VPS (como o plano *Always Free* da Oracle Cloud com arquitetura ARM ou instâncias EC2 da AWS) fornece controle absoluto sobre o servidor e os recursos computacionais. 

Nesta abordagem, o gerenciamento do sistema operacional Linux, do Docker e da exposição de portas fica sob responsabilidade do administrador.

### Integração Contínua (CI/CD) com GitHub Actions

O repositório já conta com um workflow estruturado na pasta `.github/workflows/deploy.yml` para automatizar as atualizações na VPS. 

Para ativar o deploy automatizado via SSH:

1. Acesse o seu servidor VPS e instale o motor do **Docker**.
2. No repositório do GitHub, acesse a aba **Settings > Secrets and variables > Actions**.
3. Cadastre as seguintes chaves secretas necessárias para a ponte de comunicação:
   * `ORACLE_SERVER_IP`: O endereço IP público da sua VPS.
   * `ORACLE_SERVER_USER`: O usuário do sistema operacional (ex: `ubuntu` ou `opc`).
   * `ORACLE_SSH_PRIVATE_KEY`: A chave privada SSH de acesso ao servidor.
   * `NEON_DATABASE_URL`: A string de conexão do seu banco de dados em produção.
   * `DJANGO_SECRET_KEY`: A sua chave criptográfica do projeto.

Ao realizar um comando `git push` para a *branch* principal (`main` ou `master`), o GitHub Actions assumirá o controle. Ele conectará no seu servidor remotamente, fará o download da versão mais recente do código, reconstruirá a imagem baseada no `Dockerfile` e reiniciará a aplicação sem intervenção manual.