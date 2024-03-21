---
sidebar_position: 4
---

# Updating documentation

For large functionality changes, please remember to update `mephisto.ai` documentation.

We use Docusaurus package to make Markdown docs available on the web.

## Run locally

To run Mephisto docs on your local machine, run these commands:

```bash
cd /mephisto/docs/web/
yarn
yarn install
yarn info --name-only
yarn start:docker
```

You will now be able to access docs in the browser on [http://localhost:3001/](http://localhost:3001/)
