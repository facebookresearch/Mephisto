import { feedbackClassNamePrefix } from "../../helper";

const feedbackTextError = "This is toooooo long";
const feedbackText = "🥳 This text should pass";
describe("Loads static_react_task_with_tips", () => {
  it("Feedback component contains correct react elements", () => {
    cy.visit("/");
    cy.get(`#${feedbackClassNamePrefix}text-area`);
    cy.get(`.${feedbackClassNamePrefix}button`).should("be.disabled");
  });

  it("Checking if feedback text is too long", () => {
    cy.visit("/");
    cy.get(`#${feedbackClassNamePrefix}text-area`).as("feedbackTextArea");
    cy.get("@feedbackTextArea").type(feedbackTextError);
    cy.get("@feedbackTextArea").should("have.value", feedbackTextError);
    cy.get(`.${feedbackClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your feedback message is too long"
    );

    cy.get(`.${feedbackClassNamePrefix}button`).should("be.disabled");
  });
  it("Submitting feedback", () => {
    cy.intercept({ pathname: "/submit_metadata" }).as("submitMetadataRequest");
    cy.visit("/");
    cy.get(`#${feedbackClassNamePrefix}text-area`).as("feedbackTextArea");
    cy.get("@feedbackTextArea").type(feedbackText);
    cy.get("@feedbackTextArea").should("have.value", feedbackText);
    cy.get(`.${feedbackClassNamePrefix}button`).as("submitButton");

    cy.get("@submitButton").should("not.be.disabled");
    cy.get("@submitButton").click();
    cy.wait("@submitMetadataRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
    cy.get(`.${feedbackClassNamePrefix}green-box`).should(
      "have.text",
      "✅ Your feedback has been submitted for review"
    );
    cy.get("@feedbackTextArea").should("have.value", "");
    cy.get("@submitButton").should("be.disabled");
  });
});
