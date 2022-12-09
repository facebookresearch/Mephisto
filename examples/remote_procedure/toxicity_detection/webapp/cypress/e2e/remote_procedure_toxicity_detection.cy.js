describe("Loads remote_procedure_toxicity_detection", () => {
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
    cy.get('[data-cy="detection-text-area"]');
    cy.get('[data-cy="submit-button"]');
  });

  it("Typing and submitting a toxic statement", () => {
    cy.get('[data-cy="detection-text-area"]').as("textArea");
    cy.get('[data-cy="submit-button"]').as("submitButton");

    cy.get("@textArea").type("I hate bob!");
    cy.get("@submitButton").click();
    cy.get('[data-cy="loading-spinner"]');
    // This timeout is 80000 because the detoxify model takes a good bit of time to run
    cy.get('[data-cy="toxicity-alert"]', { timeout: 80000 }).as(
      "toxicityAlert"
    );
    cy.get("@toxicityAlert").contains(
      'The statement, "I hate bob!," has a toxicity of:'
    );
  });

  it("Typing and submitting a non-toxic statement", () => {
    cy.intercept({ pathname: "/submit_task" }).as("submitTaskRequest");
    cy.on("window:alert", (text) => {
      expect(text).to.contains(
        'The task has been submitted! Data: {"toxicity":'
      );
    });
    cy.get('[data-cy="detection-text-area"]').as("textArea");
    cy.get('[data-cy="submit-button"]').as("submitButton");

    cy.get("@textArea").type("I love pizza!");
    cy.get("@submitButton").click();
    cy.get('[data-cy="loading-spinner"]');
    cy.wait("@submitTaskRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
    cy.get('[data-cy="loading-spinner"]').should("not.be.exist");
  });
});
