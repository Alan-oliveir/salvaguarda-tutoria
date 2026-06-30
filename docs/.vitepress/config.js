export default {
  base: "/",
  title: "Salvaguarda Tutoria",
  description: "Plataforma de Apoio e Gestão Educacional",
  themeConfig: {
    logo: "/logo.png",
    nav: [
      { text: "Início", link: "/" },
      { text: "Guia do Tutorado", link: "/tutorado/primeiro-acesso" },
      { text: "Guia do Tutor", link: "/tutor/uso-plataforma" },
    ],
    sidebar: {
      "/tutorado/": [
        {
          text: "Área do Tutorado",
          items: [
            {
              text: "Primeiro Acesso & Perfil",
              link: "/tutorado/primeiro-acesso",
            },
            { text: "Agendando Reuniões", link: "/tutorado/agendamentos" },
            {
              text: "Tarefas e Materiais",
              link: "/tutorado/tarefas-materiais",
            },
          ],
        },
      ],
      "/tutor/": [
        {
          text: "Operação do Tutor",
          items: [
            {
              text: "Painel e Gestão de Alunos",
              link: "/tutor/uso-plataforma",
            },
            { text: "Agenda e Reuniões", link: "/tutor/agenda-reunioes" },
            {
              text: "Tarefas e Carga Horária",
              link: "/tutor/tarefas-relatorios",
            },
          ],
        },
        {
          text: "Espaço do Desenvolvedor",
          items: [
            { text: "Instalação Local", link: "/tutor/instalacao-local" },
            { text: "Deploy em Produção", link: "/tutor/deploy-nuvem" },
          ],
        },
      ],
    },
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/Alan-oliveir/salvaguarda-tutoria",
      },
    ],
  },
};