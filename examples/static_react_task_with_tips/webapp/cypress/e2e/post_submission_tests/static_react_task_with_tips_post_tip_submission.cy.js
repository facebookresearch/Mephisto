import { tipClassNamePrefix } from "../../helper";
describe("Checking for tips", () => {
  // Checks if the two most recent tips are what was submitted in the pre_tip_submission test
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
    /* cy.get(`.${tipClassNamePrefix}tip`).eq(-1).as("lastTip");

    cy.get("@lastTip").find("h2").as("lastTipHeader");
    cy.get("@lastTip").find("p").as("lastTipBody");

    cy.get("@lastTipHeader").should(
      "have.text",
      "This is my second tip header"
    );
    cy.get("@lastTipBody").should("have.text", "This is my second tip body"); */
  });
});
