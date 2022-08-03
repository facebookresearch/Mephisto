describe("Loads simple_static_task", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Loads correct elements", () => {
    cy.get('[data-cy="close-modal-button"]');
    cy.get('[data-cy="instructions-panel-header"]');
    cy.get('[data-cy="instructions-panel-body"]');
    cy.get('[data-cy="character-name-paragraph"]');
    cy.get('[data-cy="character-description-paragraph"]');
    cy.get('[data-cy="character-dropdown"]');
    cy.get('[data-cy="submit-button"]');
  });
});

describe("Submits the html_static_task", () => {
  it("Closing starting modal", () => {
    cy.get('[data-cy="close-modal-button"]').as("modalButton").click();
    cy.get("@modalButton").should("not.be.visible");
  });
  it("Select a character name description", () => {
    cy.get('[data-cy="character-dropdown"]').select("Good");
    cy.get('[data-cy="character-dropdown"]').select("Bad");
  });
  it("Upload a file", () => {
    cy.fixture("bliss.png").then((fileContent) => {
      cy.get('[data-cy="character-file-input"]').attachFile({
        fileContent: fileContent.toString(),
        fileName: "bliss.png",
        mimeType: "image/png",
      });
    });
  });
  it("Submit the task", () => {
    cy.on("window:alert", (txt) => {
      expect(txt).to.contains(
        'The task has been submitted! Data: {"rating":"bad"'
      );
      expect(txt).to.contains('"name":"bliss.png"');
      expect(txt).to.contains('"size":51824');
      expect(txt).to.contains('"type":"image/png"');
    });
    cy.intercept({ pathname: "/submit_task" }).as("submitTask");
    cy.get('[data-cy="submit-button"]').click();
    cy.wait("@submitTask").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
});
