describe("Checking for tips", () => {
  it("Checks for recently added tip", () => {
    cy.visit("/");
    cy.get(".mephisto-worker-experience-tips__button").as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(".mephisto-worker-experience-tips__tip").last().as("lastTip");
    cy.get("@lastTip").find("h2").as("lastTipHeader");
    cy.get("@lastTip").find("p").as("lastTipBody");

    cy.get("@lastTipHeader").should(
      "have.text",
      "🎉 This is my test tip header"
    );

    cy.get("@lastTipBody").should("have.text", "🎈 This is my test tip body");
  });
});
