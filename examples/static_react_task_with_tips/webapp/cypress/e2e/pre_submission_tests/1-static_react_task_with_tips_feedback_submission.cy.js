import { feedbackClassNamePrefix } from "../../helper";

const feedbackTextError =
  "This is toooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo long";
const feedbackText1 = "🥳 First question should pass";
const feedbackText2 = "🎉 Second question should pass";
const question1 = "What is your favorite part of this task?";
const question2 = "Were you satisfied with this task?";

describe("Loads static_react_task_with_tips", () => {
  it("Feedback component contains correct react elements", () => {
    cy.visit("/");
    cy.get(`.${feedbackClassNamePrefix}header1`);
    cy.get(`.${feedbackClassNamePrefix}subtitle`);
    // Getting question labels
    cy.get(`.${feedbackClassNamePrefix}question`)
      .first()
      .should("have.text", question1);
    cy.get(`.${feedbackClassNamePrefix}question`)
      .last()
      .should("have.text", question2);

    // Getting question text areas
    cy.get("#question-0");
    cy.get("#question-1");

    cy.get(`.${feedbackClassNamePrefix}button`).should("be.disabled");
  });

  it("Checking if feedback text is too long", () => {
    cy.visit("/");
    cy.get("#question-0").as("firstFeedbackTextArea");
    cy.get("@firstFeedbackTextArea").type(feedbackTextError);
    cy.get("@firstFeedbackTextArea").should("have.value", feedbackTextError);
    cy.get(`.${feedbackClassNamePrefix}red-box`)
      .first()
      .should(
        "have.text",
        "📝 Your feedback message for this question is too long"
      );

    cy.get("#question-1").as("secondFeedbackTextArea");
    cy.get("@secondFeedbackTextArea").type(feedbackTextError);
    cy.get("@secondFeedbackTextArea").should("have.value", feedbackTextError);
    cy.get(`.${feedbackClassNamePrefix}red-box`)
      .last()
      .should(
        "have.text",
        "📝 Your feedback message for this question is too long"
      );
    cy.get(`.${feedbackClassNamePrefix}button`).should("be.disabled");
    cy.get("@firstFeedbackTextArea").clear();
    cy.get("@secondFeedbackTextArea").clear();
    cy.get(`.${feedbackClassNamePrefix}button`).should("be.disabled");
  });
  it("Submitting feedback", () => {
    cy.intercept({ pathname: "/submit_metadata" }).as("submitMetadataRequest");
    cy.visit("/");
    cy.get(`#question-0`).as("firstFeedbackTextArea");
    cy.get(`#question-1`).as("secondFeedbackTextArea");
    cy.get("@firstFeedbackTextArea").type(feedbackText1);
    cy.get("@firstFeedbackTextArea").should("have.value", feedbackText1);
    cy.get("@secondFeedbackTextArea").type(feedbackText2);
    cy.get("@secondFeedbackTextArea").should("have.value", feedbackText2);

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
    cy.get("@firstFeedbackTextArea").should("have.value", "");
    cy.get("@secondFeedbackTextArea").should("have.value", "");
    cy.get("@submitButton").should("be.disabled");
  });
});
