describe("Loads remote_procedure_template", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Loads correct react elements", () => {
    cy.get('[data-cy="directions-header"]');
    cy.get('[data-cy="directions-paragraph"]');
    cy.get('[data-cy="query-backend-button"]');
    cy.get('[data-cy="submit-button"]');
  });

  it("Submit button not disabled after querying backend four times", () => {
    cy.on("window:alert", (txt) => {
      expect(txt).to.contain("this was request");
    });

    cy.get('[data-cy="query-backend-button"]').as("queryBackendButton");
    cy.get('[data-cy="submit-button"]').as("submitButton");

    // These ugly wait statements exist because cypress doesn't handle react-rerenders well
    // https://github.com/cypress-io/cypress/issues/7306
    cy.get("@submitButton").should("be.disabled");

    cy.get("@queryBackendButton").should("be.visible");

    cy.get("@queryBackendButton").click();

    cy.get("@submitButton").should("be.disabled");

    cy.wait(1000);
    cy.get("@queryBackendButton").should("be.visible");
    cy.get("@queryBackendButton").click();

    cy.get("@submitButton").should("be.disabled");

    cy.wait(1000);
    cy.get("@queryBackendButton").should("be.visible");
    cy.get("@queryBackendButton").click();

    cy.get("@submitButton").should("be.disabled");

    cy.wait(1000);
    cy.get("@queryBackendButton").should("be.visible");
    cy.get("@queryBackendButton").click();

    cy.wait(1000);
    cy.get("@submitButton").should("not.be.disabled");
  });
});
