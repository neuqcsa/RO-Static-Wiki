import { DefaultTheme, defineConfig } from 'vitepress';
import { pagefindPlugin } from 'vitepress-plugin-pagefind'
const docs = require("../docs.json")
/**
 * Convert feishu-pages's docs.json into VitePress's sidebar config
 * @param docs from `docs.json`
 * @returns
 */
const convertDocsToSidebars = (docs: any) => {
  const sidebars: DefaultTheme.SidebarItem[] = [];
  for (const doc of docs) {
    let sidebar: DefaultTheme.SidebarItem = {
      text: doc.title,
      link: doc.slug,
      collapsed: true
    };
    if (doc.children.length > 0) {
      sidebar.items = convertDocsToSidebars(doc.children);
    }
    sidebars.push(sidebar);
  }

  return sidebars;
};


export default defineConfig({
  title: "NEUQRO 静态知识库",
  ignoreDeadLinks: true,
  themeConfig: {
    sidebar: convertDocsToSidebars(docs),
    nav: [
      { text: '首页', link: '/' },
      { text: '在线知识库', link: 'https://neuqro-team.feishu.cn/wiki/' },
      { text: 'GitHub', link: 'https://github.com/neuqcsa/RO-Static-Wiki' }
    ],
    docFooter: {
      prev: false,
      next: false
    },
    search: {
      provider: 'local'
    }
  },
  markdown: {
    config: (md) => {
      md.disable('emoji', true);
      const render = md.render
      md.render = function (src, env) {
        return `<div v-pre>${render.call(this, src, env)}</div>`
      }
    },
    html: true,
    attrs: {
      disable: true
    }
  },
  vite: {
    plugins: [pagefindPlugin()],
  }
  // themeConfig: {
  //   // https://vitepress.dev/reference/default-theme-config
  //   nav: [
  //     { text: 'Home', link: '/' },
  //     { text: 'Examples', link: '/markdown-examples' }
  //   ],

  //   sidebar: [
  //     {
  //       text: 'Examples',
  //       items: [
  //         { text: 'Markdown Examples', link: '/markdown-examples' },
  //         { text: 'Runtime API Examples', link: '/api-examples' }
  //       ]
  //     }
  //   ],

  //   socialLinks: [
  //     { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
  //   ]
  // }
});

// import { defineConfig } from 'vitepress'

// // https://vitepress.dev/reference/site-config
// export default defineConfig({
//   title: "My Awesome Project",
//   description: "A VitePress Site",
//   themeConfig: {
//     // https://vitepress.dev/reference/default-theme-config
//     nav: [
//       { text: 'Home', link: '/' },
//       { text: 'Examples', link: '/markdown-examples' }
//     ],

//     sidebar: [
//       {
//         text: 'Examples',
//         items: [
//           { text: 'Markdown Examples', link: '/markdown-examples' },
//           { text: 'Runtime API Examples', link: '/api-examples' }
//         ]
//       }
//     ],

//     socialLinks: [
//       { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
//     ]
//   }
// })
