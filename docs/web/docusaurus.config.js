/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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

  themes: [
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      ({
        indexDocs: true,
        indexBlog: true,
        // `hashed` is recommended as long-term-cache of index file is possible.
        hashed: true,
        language: ["en"],
        highlightSearchTermsOnTargetPage: true,
        searchResultLimits: 8,
        // Set the max length of characters of each search result to show.
        searchResultContextMaxLength: 50,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
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
            docId: "explanations/abstractions_overview",
            position: "left",
            label: "Explanations",
          },
          {
            type: "doc",
            docId: "reference/overview",
            position: "left",
            label: "Reference",
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
                to: "/docs/explanations/abstractions_overview",
              },
              {
                label: "Reference",
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
              {
                label: "Terms of Use",
                href: "https://opensource.fb.com/legal/terms/",
              },
              {
                label: "Privacy",
                href: "https://opensource.fb.com/legal/privacy/",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Meta Platforms. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
