const { defineConfig } = require("cypress");

module.exports = defineConfig({
  video: false,

  e2e: {
    baseUrl: "http://localhost:3000/?worker_id=x&assignment_id=1",
    /* setupNodeEvents(on, config) {
      // implement node event listeners here
    }, */
  },
});
