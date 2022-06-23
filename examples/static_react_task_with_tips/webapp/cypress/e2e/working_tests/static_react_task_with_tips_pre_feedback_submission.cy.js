const feedbackTextError =
  "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉";
const feedbackText = "🥳 This text should pass";
describe("Loads static_react_task_with_tips", () => {
  it("Feedback component contains correct react elements", () => {
    cy.visit("/");
    cy.get("#mephisto-worker-experience-feedback__text-area");
    cy.get(".mephisto-worker-experience-feedback__button").should(
      "be.disabled"
    );
  });

  it("Checking if feedback text is too long", () => {
    cy.visit("/");
    cy.get("#mephisto-worker-experience-feedback__text-area").as(
      "feedbackTextArea"
    );
    cy.get("@feedbackTextArea").type(feedbackTextError);
    cy.get("@feedbackTextArea").should("have.value", feedbackTextError);
    cy.get(".mephisto-worker-experience-feedback__red-box").should(
      "have.text",
      "📝 Your feedback message is too long"
    );

    cy.get(".mephisto-worker-experience-feedback__button").should(
      "be.disabled"
    );
  });
  it("Submitting feedback", () => {
    cy.intercept({ pathname: "/submit_metadata" }).as("submitMetadataRequest");
    cy.visit("/");
    cy.get("#mephisto-worker-experience-feedback__text-area").as(
      "feedbackTextArea"
    );
    cy.get("@feedbackTextArea").type(feedbackText);
    cy.get("@feedbackTextArea").should("have.value", feedbackText);
    cy.get(".mephisto-worker-experience-feedback__button").as("submitButton");

    cy.get("@submitButton").should("not.be.disabled");
    cy.get("@submitButton").click();
    cy.wait("@submitMetadataRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
    cy.get(".mephisto-worker-experience-feedback__green-box").should(
      "have.text",
      "✅ Your feedback has been submitted for review"
    );
    cy.get("@feedbackTextArea").should("have.value", "");
    cy.get("@submitButton").should("be.disabled");
  });
});
