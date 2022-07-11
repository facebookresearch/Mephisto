const pathToAssignmentId = "cypress/assignment_id.txt";

describe("Requests", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.readFile(pathToAssignmentId).then((assignmentId) => {
      cy.visit("/?worker_id=x&assignment_id=" + assignmentId);
    });
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
});

describe("Loading & Interactive With Content", () => {
  beforeEach(() => {
    cy.readFile(pathToAssignmentId).then((assignmentId) => {
      cy.visit("/?worker_id=x&assignment_id=" + assignmentId);
    });
  });

  it("Loads correct react elements", () => {
    cy.get('[data-cy="directions-container"]');
    cy.get('[data-cy="task-data-text"]');
    cy.get('[data-cy="good-button"]');
    cy.get('[data-cy="bad-button"]');
  });
  it("Gets request from pressing good button", () => {
    cy.intercept({ pathname: "/submit_task" }).as("goodTaskSubmit");
    cy.get('[data-cy="good-button"]').click();
    cy.wait("@goodTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Shows alert from pressing good button", () => {
    cy.on("window:alert", (txt) => {
      expect(txt).to.contains(
        'The task has been submitted! Data: {"rating":"good"}'
      );
    });
    cy.get('[data-cy="good-button"]').click();
  });

  it("Gets request from pressing bad button", () => {
    cy.intercept({ pathname: "/submit_task" }).as("badTaskSubmit");
    cy.get('[data-cy="bad-button"]').click();
    cy.wait("@badTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Shows alert from pressing bad button", () => {
    cy.on("window:alert", (txt) => {
      expect(txt).to.contains(
        'The task has been submitted! Data: {"rating":"bad"}'
      );
    });
    cy.get('[data-cy="bad-button"]').click();
  });
});
