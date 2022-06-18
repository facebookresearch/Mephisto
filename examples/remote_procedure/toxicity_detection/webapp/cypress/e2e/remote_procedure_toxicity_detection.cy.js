describe("Loads remote_procedure_toxicity_detection", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("http://localhost:3000/?worker_id=x&assignment_id=31");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Loads correct react elements", () => {
    cy.visit("http://localhost:3000/?worker_id=x&assignment_id=31");
    cy.get('[data-cy="directions-header"]');
    cy.get('[data-cy="directions-paragraph"]');
    cy.get('[data-cy="detection-text-area"]');
    cy.get('[data-cy="submit-button"]');
  });

  it("Typing and submitting a toxic statement", () => {
    cy.visit("http://localhost:3000/?worker_id=x&assignment_id=31");
    cy.get('[data-cy="detection-text-area"]').as("textArea");
    cy.get('[data-cy="submit-button"]').as("submitButton");

    cy.get("@textArea").type("I hate bob!");
    cy.get("@submitButton").click();
    cy.get('[data-cy="loading-spinner"]');
    cy.wait(10000);
    cy.get('[data-cy="loading-spinner"]').should("not.be.exist");
    cy.get('[data-cy="toxicity-alert"]').as("toxicityAlert");
    cy.get("@toxicityAlert");
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
    cy.visit("http://localhost:3000/?worker_id=x&assignment_id=31");
    cy.get('[data-cy="detection-text-area"]').as("textArea");
    cy.get('[data-cy="submit-button"]').as("submitButton");

    cy.get("@textArea").type("I love pizza!");
    cy.get("@submitButton").click();
    cy.get('[data-cy="loading-spinner"]');
    cy.wait("@submitTaskRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
    cy.wait(4000);
    cy.get('[data-cy="loading-spinner"]').should("not.be.exist");
  });
});
