// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Mephisto",
  tagline: "Bring your research ideas to life with effective data annotation",
  url: "https://mephisto.ai/",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.png",
  organizationName: "facebookresearch",
  projectName: "mephisto",
  trailingSlash: true,

  presets: [
    [
      "@docusaurus/preset-classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl:
            "https://github.com/facebookresearch/Mephisto/tree/main/docs/web/",
        },
        blog: {
          showReadingTime: true,
          editUrl:
            "https://github.com/facebookresearch/Mephisto/tree/main/docs/web/blog/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      algolia: {
        // The application ID provided by Algolia
        appId: "J6ARWT70HK",

        // Public API key: it is safe to commit it
        apiKey: "ac51a5b25842fad8a3a7b1f384496bf9",

        indexName: "mephisto",
        searchPagePath: false,
      },
      navbar: {
        // title: "Mephisto",
        logo: {
          alt: "Mephisto",
          src: "img/logo.svg",
          srcDark: "img/logo_w.svg",
        },
        items: [
          {
            type: "doc",
            docId: "guides/quickstart",
            position: "left",
            label: "Guides",
          },
          {
            type: "doc",
            docId: "explanations/architecture_overview",
            position: "left",
            label: "Explanations",
          },
          {
            type: "doc",
            docId: "reference/overview",
            position: "left",
            label: "API Reference",
          },
          { to: "/blog", label: "Blog", position: "left" },
          {
            href: "https://github.com/facebookresearch/Mephisto",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              {
                label: "Guides",
                to: "/docs/guides/quickstart",
              },
              {
                label: "Explanations",
                to: "/docs/explanations/architecture_overview",
              },
              {
                label: "API Reference",
                to: "/docs/reference/overview",
              },
            ],
          },
          {
            title: "Community",
            items: [
              {
                label: "Stack Overflow",
                href: "https://stackoverflow.com/questions/tagged/mephisto",
              },
              // {
              //   label: "Discord",
              //   href: "https://discordapp.com/invite/docusaurus",
              // },
              // {
              //   label: "Twitter",
              //   href: "https://twitter.com/docusaurus",
              // },
            ],
          },
          {
            title: "More",
            items: [
              // {
              //   label: "Blog",
              //   to: "/blog",
              // },
              {
                label: "GitHub",
                href: "https://github.com/facebookresearch/Mephisto",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()}. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
