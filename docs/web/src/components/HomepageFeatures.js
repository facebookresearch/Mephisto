import React from "react";
import clsx from "clsx";
import styles from "./HomepageFeatures.module.css";

const FeatureList = [
  {
    title: "Platform-Agnostic",
    Svg: require("../../static/img/undraw_docusaurus_mountain.svg").default,
    description: (
      <>
        Mephisto was designed from the ground up to work with different "crowd
        providers". You can use Amazon Mechanical Turk, an internal platform for
        your organization, or something else. Additionally, launch your tasks on
        Heroku, EC2, etc.
      </>
    ),
  },
  {
    title: "Centralization",
    Svg: require("../../static/img/undraw_docusaurus_tree.svg").default,
    description: (
      <>
        Share blocklists and track worker utilization across multiple projects.
      </>
    ),
  },
  {
    title: "Extensible",
    Svg: require("../../static/img/undraw_docusaurus_react.svg").default,
    description: (
      <>
        Mephisto defines tasks in "blueprints". Publish, share, and re-use them
        to get up and running quickly!
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      {/* <div className="text--center">
        <Svg className={styles.featureSvg} alt={title} />
      </div> */}
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
