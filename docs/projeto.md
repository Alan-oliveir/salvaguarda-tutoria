# Salvaguarda - Plataforma de Apoio Educacional

**Salvaguarda** é uma aplicação web voltada para a gestão de tutorados em um programa educacional voluntário. O sistema facilita o acompanhamento de estudantes por tutores, promovendo organização, comunicação e apoio contínuo ao desenvolvimento acadêmico dos participantes.

---

## Objetivos

- Gerenciar tutorados de forma personalizada e eficiente
- Acompanhar reuniões, tarefas e progresso de cada estudante
- Oferecer uma interface acessível e segmentada para administradores, tutores e tutorados

---

## Perfis de Usuário

### Administrador
- Gerencia o sistema e os usuários
- Cadastra tutores
- Visualiza relatórios globais

### Tutor
- Cadastra e gerencia seus próprios tutorados
- Agenda reuniões, envia tarefas e materiais
- Acompanha o progresso de cada tutorado

### Tutorado
- Acessa seu painel pessoal
- Visualiza tarefas, reuniões, progresso e materiais

---

## Funcionalidades

### Autenticação e Perfis
- Login e cadastro por tipo de usuário
- Sistema de permissões
- Interface personalizada por perfil

### Gestão de Tutorados
- Cadastro de tutorados realizado pelo tutor
- Campos personalizados:
  - Foto (opcional), Estado, Cidade, Série, Idade
  - Já fez o ENEM (sim/não)
  - Cursos de interesse, WhatsApp, Email

### Reuniões e Histórico
- Agendamento com data, horário e link (Google Meet, Zoom, etc.)
- Histórico de reuniões com tópicos, duração, observações e presença

### Tarefas
- Criação de tarefas com descrição, status e prazo
- Tutorados marcam como concluídas

### Materiais
- Upload e visualização de arquivos por tutores e tutorados

### Painel de Progresso
- Gráficos e indicadores de:
  - Tarefas concluídas
  - Reuniões realizadas
  - Frequência e engajamento

---

## Melhorias Futuras

- Mensagens internas entre tutor e tutorado
- Feedbacks personalizados após reuniões e tarefas
- Integração com Google Meet ou Zoom
- Notificações por email
- Exportação de relatórios em PDF

---

## Tecnologias Recomendadas

- **Backend:** Django + Django REST Framework
- **Frontend:** Django Templates ou React (futuro)
- **Banco de Dados:** SQLite
- **Gráficos:** Chart.js, Recharts
- **Deploy:** Render, Railway ou Fly.io

---

## Status do Projeto

Em desenvolvimento | Módulos iniciais concluídos:
- Autenticação com perfis
- Painel dinâmico por tipo de usuário
- Design inicial com identidade visual
