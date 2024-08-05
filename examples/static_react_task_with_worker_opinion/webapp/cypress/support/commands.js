/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { workerOpinionClassNamePrefix } from "../helper";
/*
  Defines the submitTip command to allow
  for code reuse
*/
Cypress.Commands.add("submitTip", (tipHeader, tipBody) => {
  // TODO: Fix tests for WorkerOpinion widget
  // cy.get("@tipsHeaderInput").type(tipHeader, { force: true });
  // cy.get("@tipsBodyInput").type(tipBody, { force: true });
  // cy.get("@submitButton").should("not.be.disabled");
  // cy.get("@tipsHeaderInput").should("have.value", tipHeader);
  // cy.get("@tipsBodyInput").should("have.value", tipBody);
  //
  // cy.get("@submitButton").click();
  //
  // cy.wait("@submitMetadataRequest").then((interception) => {
  //   expect(interception.response.statusCode).to.eq(200);
  // });
  //
  // cy.get("@tipsHeaderInput").should("have.value", "");
  // cy.get("@tipsBodyInput").should("have.value", "");
  // cy.get("@submitButton").should("be.disabled");
  // cy.get(`.${workerOpinionClassNamePrefix}green-box`).should(
  //   "have.text",
  //   "✅ Your tip has been submitted for review"
  // );
  // cy.get("@tipsHeaderInput").should("have.value", "");
  // cy.get("@tipsBodyInput").should("have.value", "");
  // cy.get("@submitButton").should("be.disabled");
});
