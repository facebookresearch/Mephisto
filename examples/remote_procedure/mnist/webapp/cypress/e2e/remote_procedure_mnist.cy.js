/*
  Not really sure how to test react-canvas-draw
  so the test is kind of incomplete
*/

describe("Loads remote_procedure_mnist", () => {
  Cypress.on("uncaught:exception", (err, runnable) => {
    return false;
  });

  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Loads correct react elements", () => {
    cy.visit("/");
    cy.get('[data-cy="canvas-container-0"]');
    cy.get('[data-cy="clear-button-0"]');
    cy.get('[data-cy="correct-checkbox-0"]');
    cy.get('[data-cy="correct-text-input-0"]');

    cy.get('[data-cy="canvas-container-1"]');
    cy.get('[data-cy="clear-button-1"]');
    cy.get('[data-cy="correct-checkbox-1"]');
    cy.get('[data-cy="correct-text-input-1"]');

    cy.get('[data-cy="canvas-container-2"]');
    cy.get('[data-cy="clear-button-2"]');
    cy.get('[data-cy="correct-checkbox-2"]');
    cy.get('[data-cy="correct-text-input-2"]');

    cy.get('[data-cy="submit-button"]').as("submitButton");
    cy.get("@submitButton").should("be.disabled");
  });

  it("Submitting with three corrected annotations", () => {
    cy.visit("/");
    cy.get('[data-cy="clear-button-0"]').as("clearButton0");
    cy.get('[data-cy="clear-button-1"]').as("clearButton1");
    cy.get('[data-cy="clear-button-2"]').as("clearButton2");

    cy.get('[data-cy="correct-checkbox-0"]').should("be.disabled");
    cy.get('[data-cy="correct-text-input-0"]').should("be.disabled");

    cy.get('[data-cy="correct-checkbox-1"]').should("be.disabled");
    cy.get('[data-cy="correct-text-input-1"]').should("be.disabled");

    cy.get('[data-cy="correct-checkbox-2"]').should("be.disabled");
    cy.get('[data-cy="correct-text-input-2"]').should("be.disabled");

    cy.get("@clearButton0").should("be.visible");
    cy.get("@clearButton0").click({ force: true });

    cy.get("@clearButton1").should("be.visible");
    cy.get("@clearButton1").click({ force: true });

    cy.get("@clearButton2").should("be.visible");
    cy.get("@clearButton2").click({ force: true });
  });
});
