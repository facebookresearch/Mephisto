import { tipClassNamePrefix } from "../helper";
/*
  Defines the submitTip command to allow
  for code reuse
*/
Cypress.Commands.add("submitTip", (tipHeader, tipBody) => {
  cy.get("@tipsHeaderInput").type(tipHeader, { force: true });
  cy.get("@tipsBodyInput").type(tipBody, { force: true });
  cy.get("@submitButton").should("not.be.disabled");
  cy.get("@tipsHeaderInput").should("have.value", tipHeader);
  cy.get("@tipsBodyInput").should("have.value", tipBody);

  cy.get("@submitButton").click();

  cy.wait("@submitMetadataRequest").then((interception) => {
    expect(interception.response.statusCode).to.eq(200);
  });

  cy.get("@tipsHeaderInput").should("have.value", "");
  cy.get("@tipsBodyInput").should("have.value", "");
  cy.get("@submitButton").should("be.disabled");
  cy.get(`.${tipClassNamePrefix}green-box`).should(
    "have.text",
    "✅ Your tip has been submitted for review"
  );
  cy.get("@tipsHeaderInput").should("have.value", "");
  cy.get("@tipsBodyInput").should("have.value", "");
  cy.get("@submitButton").should("be.disabled");
});
