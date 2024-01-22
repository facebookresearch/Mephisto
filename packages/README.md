# Mephisto Packages

Mephisto repository contains JavaScript libraries that are located in `packages` directory.
They are either part of Mephisto core functionality, or are used in sample tasks (in `examples` directory).
Most of these packages are available as `npm` packages on https://www.npmjs.com/.

## Custom packages

If you want to customize existing packages or create a new one, you can place them into `packages` directory (and update installed dependencies list in your `package.json` accrodingly). Because your custom library is available only locally (and via `npm`), you need to include it into Mephisto build under an alias in `webpack` config:

```js
var path = require("path");
var webpack = require("webpack");

// Specifies location of your packages (e.g. `../../dir`)
var PATH_TO_PACKAGES = "<path>"

module.exports = {
  ...
  resolve: {
    alias: {
      // Your custom local libraries
      "my-library": path.resolve(
        __dirname, `${PATH_TO_PACKAGES}/packages/my-library`,
      ),
    },
    fallback: {
      net: false,
      dns: false,
    },
  },
  ...
};
```

Then you can add `mylibrary` via regular imports:

```js
import { MyComponent } from "my-library";
```

For a working example of an aliased library see [webpack.config.js](/examples/form_composer_demo/webapp/webpack.config.js) from `form_composer_demo` sample project.
