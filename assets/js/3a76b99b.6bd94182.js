"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[923],{5110:function(e,t,n){n.d(t,{Zo:function(){return l},kt:function(){return m}});var r=n(9703);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,r,i=function(e,t){if(null==e)return{};var n,r,i={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var u=r.createContext({}),s=function(e){var t=r.useContext(u),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},l=function(e){var t=s(e.components);return r.createElement(u.Provider,{value:t},e.children)},c={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,i=e.mdxType,a=e.originalType,u=e.parentName,l=p(e,["components","mdxType","originalType","parentName"]),d=s(n),m=i,f=d["".concat(u,".").concat(m)]||d[m]||c[m]||a;return n?r.createElement(f,o(o({ref:t},l),{},{components:n})):r.createElement(f,o({ref:t},l))}));function m(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var a=n.length,o=new Array(a);o[0]=d;var p={};for(var u in t)hasOwnProperty.call(t,u)&&(p[u]=t[u]);p.originalType=e,p.mdxType="string"==typeof e?e:i,o[1]=p;for(var s=2;s<a;s++)o[s]=n[s];return r.createElement.apply(null,o)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},5245:function(e,t,n){n.r(t),n.d(t,{contentTitle:function(){return u},default:function(){return d},frontMatter:function(){return p},metadata:function(){return s},toc:function(){return l}});var r=n(2922),i=n(9230),a=(n(9703),n(5110)),o=["components"],p={sidebar_position:1},u="Upgrade Guide",s={unversionedId:"guides/upgrade_to_1/guide",id:"guides/upgrade_to_1/guide",isDocsHomePage:!1,title:"Upgrade Guide",description:"1. Update the Mephisto library to v1.",source:"@site/docs/guides/upgrade_to_1/guide.md",sourceDirName:"guides/upgrade_to_1",slug:"/guides/upgrade_to_1/guide",permalink:"/docs/guides/upgrade_to_1/guide",editUrl:"https://github.com/facebookresearch/Mephisto/tree/main/docs/web/docs/guides/upgrade_to_1/guide.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1},sidebar:"guides",previous:{title:"Backend: dev setup",permalink:"/docs/guides/how_to_contribute/backend_development"},next:{title:"Migrating Run Scripts",permalink:"/docs/guides/upgrade_to_1/run_scripts"}},l=[],c={toc:l};function d(e){var t=e.components,n=(0,i.Z)(e,o);return(0,a.kt)("wrapper",(0,r.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"upgrade-guide"},"Upgrade Guide"),(0,a.kt)("ol",null,(0,a.kt)("li",{parentName:"ol"},"Update the Mephisto library to v1.",(0,a.kt)("ul",{parentName:"li"},(0,a.kt)("li",{parentName:"ul"},"If you set up Mephisto using ",(0,a.kt)("inlineCode",{parentName:"li"},"pip install -e"),", ensure you pull the latest version down from the git repo."),(0,a.kt)("li",{parentName:"ul"},"Or if you set up Mephisto using the pip wheel: ",(0,a.kt)("inlineCode",{parentName:"li"},"pip install Mephisto -U")))),(0,a.kt)("li",{parentName:"ol"},"Ensure that your front-end code is using the latest packages, by running the following ",(0,a.kt)("strong",{parentName:"li"},"in your task's webapp folder"),".",(0,a.kt)("pre",{parentName:"li"},(0,a.kt)("code",{parentName:"pre",className:"language-bash"},"npm install --save mephisto-task@2\nnpm install --save bootstrap-chat@2 # if applicable\n"))),(0,a.kt)("li",{parentName:"ol"},"For webapps using ",(0,a.kt)("inlineCode",{parentName:"li"},"mephisto-task"),": Migrate any usage of ",(0,a.kt)("inlineCode",{parentName:"li"},"sendMessage")," in your front-end code to ",(0,a.kt)("inlineCode",{parentName:"li"},"sendLiveUpdate"),".   "),(0,a.kt)("li",{parentName:"ol"},(0,a.kt)("a",{parentName:"li",href:"../run_scripts"},"Migrate your run scripts")," to use the newly introduced syntax, aimed to reduce boilerplate.")),(0,a.kt)("div",{className:"admonition admonition-info alert alert--info"},(0,a.kt)("div",{parentName:"div",className:"admonition-heading"},(0,a.kt)("h5",{parentName:"div"},(0,a.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,a.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,a.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M7 2.3c3.14 0 5.7 2.56 5.7 5.7s-2.56 5.7-5.7 5.7A5.71 5.71 0 0 1 1.3 8c0-3.14 2.56-5.7 5.7-5.7zM7 1C3.14 1 0 4.14 0 8s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm1 3H6v5h2V4zm0 6H6v2h2v-2z"}))),"info")),(0,a.kt)("div",{parentName:"div",className:"admonition-content"},(0,a.kt)("p",{parentName:"div"},(0,a.kt)("em",{parentName:"p"},"Optional"),": If you'd like to set up metrics, you can also run the CLI command: ",(0,a.kt)("inlineCode",{parentName:"p"},"mephisto metrics install")))))}d.isMDXComponent=!0},2922:function(e,t,n){function r(){return r=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var n=arguments[t];for(var r in n)Object.prototype.hasOwnProperty.call(n,r)&&(e[r]=n[r])}return e},r.apply(this,arguments)}n.d(t,{Z:function(){return r}})},9230:function(e,t,n){function r(e,t){if(null==e)return{};var n,r,i={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(i[n]=e[n]);return i}n.d(t,{Z:function(){return r}})}}]);