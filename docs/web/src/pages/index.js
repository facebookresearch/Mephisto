import React from "react";
import clsx from "clsx";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import styles from "./index.module.css";
import HomepageFeatures from "../components/HomepageFeatures";
import { DocSearch } from "@docsearch/react";
import "@docsearch/css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <img src="/img/logo_w.svg" style={{ width: 200, marginBottom: 50 }} />
        <h1 className="">
          Bring your research ideas to life
          <br />
          with powerful crowdsourcing tooling
        </h1>
        {/* <p className="hero__subtitle">{siteConfig.tagline}</p> */}
        <div className={styles.buttons} style={{ marginTop: 50 }}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/guides/quickstart"
          >
            Quickstart - 10min ⏱️
          </Link>
          <Link
            style={{ marginLeft: 20 }}
            className="button button--secondary button--lg"
            to="https://github.com/facebookresearch/Mephisto"
          >
            Github
          </Link>
        </div>
        <div className={styles.searchBarContainer}></div>
      </div>
    </header>
  );
}
export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
