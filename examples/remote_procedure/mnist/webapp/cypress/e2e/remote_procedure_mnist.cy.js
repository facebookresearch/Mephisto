describe("Loads remote_procedure_mnist", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Loads correct react elements", () => {
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
    cy.on("window:alert", (txt) => {
      expect(txt).to.contain("The task has been submitted!");
    });

    cy.get('[data-cy="clear-button-0"]').as("clearButton0");
    cy.get('[data-cy="clear-button-1"]').as("clearButton1");
    cy.get('[data-cy="clear-button-2"]').as("clearButton2");

    // draw 4
    cy.get('[data-cy="canvas-mouse-down-container-0"]')
      .trigger("mouseover")
      .trigger("mousedown", 20, 20)
      .trigger("mousemove", 40, 150)
      .trigger("mousemove", 150, 120)
      .trigger("mousemove", 150, 10)
      .trigger("mouseup", 150, 220);

    // There is a wait statement here because it takes some time for the model to calculate that it is a 4
    cy.wait(1000);
    cy.get('[data-cy="current-annotation-0"]').should("contain.text", "4");
    cy.get('[data-cy="correct-checkbox-0"]').check();
    cy.get('[data-cy="correct-text-input-0"]').should("not.exist");

    // draw 1
    cy.get('[data-cy="canvas-mouse-down-container-1"]')
      .trigger("mouseover")
      .trigger("mousedown", 20, 60)
      .trigger("mousedown", 40, 40)
      .trigger("mousedown", 150, 30)
      .trigger("mousedown", 180, 60)
      .trigger("mousedown", 180, 120)
      .trigger("mousedown", 150, 135)
      .trigger("mousedown", 85, 145)
      .trigger("mousedown", 180, 150)
      .trigger("mousedown", 180, 210)
      .trigger("mouseup", 65, 220);

    cy.wait(1000);
    cy.get('[data-cy="current-annotation-1"]').should("contain.text", "3");
    cy.get('[data-cy="correct-checkbox-1"]').check();
    cy.get('[data-cy="correct-text-input-1]').should("not.exist");

    // draw gibberish
    cy.get('[data-cy="canvas-mouse-down-container-2"]')
      .trigger("mouseover")
      .trigger("mousedown", 10, 20)
      .trigger("mousedown", 120, 200)
      .trigger("mouseup", 120, 200);

    cy.get('[data-cy="clear-button-2"]').click();

    // draw 7
    cy.get('[data-cy="canvas-mouse-down-container-2"]')
      .trigger("mouseover")
      .trigger("mousedown", 30, 30)
      .trigger("mousedown", 220, 40)
      .trigger("mouseup", 40, 200);

    cy.get('[data-cy="correct-text-input-2"]').type("7");

    cy.get('[data-cy="submit-button"]').click({ force: true });
  });
});
