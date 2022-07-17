import { tipClassNamePrefix } from "../../helper";
describe("Checking for tips", () => {
  /*
  This test is supposed to be ran after running the pre_tip_submission cypress test.
  The pre_tip_submission cypress test submits three tips for reviewing.
  Before running this test, you should review the tips for static_react_task_with_tips
  by running python review_tips_for_task.py.

  To pass this test, accept the first tip and reject the other two.
  Then run this test and it should pass.

  The whole process is gone through in the cypress-end-to-end-tests.yml github actions file.
  */
  it("Checks for recently added tip", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`).as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(`.${tipClassNamePrefix}tip`).eq(-1).as("lastTip");

    cy.get("@lastTip").find("h2").as("lastTipHeader");
    cy.get("@lastTip").find("p").as("lastTipBody");

    cy.get("@lastTipHeader").should(
      "have.text",
      "🎉 This is my test tip header"
    );
    cy.get("@lastTipBody").should("have.text", "🎈 This is my test tip body");
  });
});
