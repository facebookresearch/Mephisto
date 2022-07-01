import { tipClassNamePrefix } from "../../helper";

const firstTipHeader = "🎉 This is my test tip header";
const firstTipBody = "🎈 This is my test tip body";

const secondTipHeader = "This is my second tip header";
const secondTipBody = "This is my second tip body";

describe("Loads static_react_task_with_tips", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Loads correct task react elements", () => {
    cy.visit("/");
    cy.get('[data-cy="directions"]');
    cy.get('[data-cy="task-text"]');
    cy.get('[data-cy="good-button"]');
    cy.get('[data-cy="bad-button"]');
  });

  it("Loads correct tip react elements", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`);
  });
});

describe("Tips Popup", () => {
  it("Opening/Closing tips popup", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`).as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(`.${tipClassNamePrefix}container`).as("tipsContainer");
    cy.get("@tipsContainer").should("exist");
    cy.get("h1").contains("Task Tips:");
    cy.get("h1").contains("Submit A Tip:");
    cy.get("label").contains("Tip Headline:");
    cy.get("label").contains("Tip Body:");
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");

    // Closing popup by clicking the hide tips button
    cy.get("@tipsButton").click();
    cy.get("@tipsContainer").should("not.exist");

    cy.get("@tipsButton").click();
    cy.get("@tipsContainer").should("exist");
    cy.get("h1").contains("Task Tips:");
    cy.get("h1").contains("Submit A Tip:");
    cy.get("label").contains("Tip Headline:");
    cy.get("label").contains("Tip Body:");
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");

    // Closing popup by clicking close button
    cy.get(`.${tipClassNamePrefix}close-icon-container`).click();
    cy.get("@tipsContainer").should("not.exist");
  });

  it("Checking if tips header is too long", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`).as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(`#${tipClassNamePrefix}header-input`).as("tipsHeaderInput");
    cy.get("@tipsHeaderInput").type("This header is tooooooooooooooooo long");
    cy.get(`.${tipClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your tip header is too long"
    );
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");
    cy.get("@tipsHeaderInput").clear();
    cy.get(`.${tipClassNamePrefix}red-box`).should("not.exist");
  });

  it("Checking if tips body is too long", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`).as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(`#${tipClassNamePrefix}text-input`).as("tipsBodyInput");
    cy.get("@tipsBodyInput").type(
      "This body is tooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo long"
    );
    cy.get(`.${tipClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your tip body is too long"
    );
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");
    cy.get("@tipsBodyInput").clear();
    cy.get(`.${tipClassNamePrefix}red-box`).should("not.exist");
  });

  it("Checking if both tips header and tips body is too long", () => {
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`).as("tipsButton");
    cy.get("@tipsButton").click();

    cy.get(`#${tipClassNamePrefix}header-input`).as("tipsHeaderInput");
    cy.get("@tipsHeaderInput").type("This header is tooooooooooooooooo long");
    cy.get(`.${tipClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your tip header is too long"
    );
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");

    cy.get(`#${tipClassNamePrefix}text-input`).as("tipsBodyInput");
    cy.get("@tipsBodyInput").type(
      "This body is tooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo long"
    );

    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");
    cy.get(`.${tipClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your tip header is too long"
    );

    cy.get("@tipsHeaderInput").clear();
    cy.get(`.${tipClassNamePrefix}red-box`).should(
      "have.text",
      "📝 Your tip body is too long"
    );
    cy.get(`.${tipClassNamePrefix}button`).should("be.disabled");

    cy.get("@tipsBodyInput").clear();
    cy.get(`.${tipClassNamePrefix}red-box`).should("not.exist");
  });

  it("Submitting a tip", () => {
    cy.intercept({ pathname: "/submit_metadata" }).as("submitMetadataRequest");
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`)
      .contains("Show Tips")
      .as("tipsButton");
    cy.get("@tipsButton").click();
    cy.get(`.${tipClassNamePrefix}button`)
      .contains("Submit Tip")
      .as("submitButton");
    cy.get("@submitButton").should("be.disabled");
    cy.get(`#${tipClassNamePrefix}header-input`).as("tipsHeaderInput");
    cy.get("@tipsHeaderInput").type(firstTipHeader);

    cy.get(`#${tipClassNamePrefix}text-input`).as("tipsBodyInput");
    cy.get("@tipsBodyInput").type(firstTipBody);
    cy.get("@submitButton").should("not.be.disabled");

    cy.get("@tipsHeaderInput").should("have.value", firstTipHeader);
    cy.get("@tipsBodyInput").should("have.value", firstTipBody);

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
  });

  it("Submitting another tip", () => {
    cy.intercept({ pathname: "/submit_metadata" }).as("submitMetadataRequest");
    cy.visit("/");
    cy.get(`.${tipClassNamePrefix}button`)
      .contains("Show Tips")
      .as("tipsButton");
    cy.get("@tipsButton").click();
    cy.get(`.${tipClassNamePrefix}button`)
      .contains("Submit Tip")
      .as("submitButton");
    cy.get("@submitButton").should("be.disabled");
    cy.get(`#${tipClassNamePrefix}header-input`).as("tipsHeaderInput");
    cy.get("@tipsHeaderInput").type(secondTipHeader);

    cy.get(`#${tipClassNamePrefix}text-input`).as("tipsBodyInput");
    cy.get("@tipsBodyInput").type(secondTipBody);
    cy.get("@submitButton").should("not.be.disabled");

    cy.get("@tipsHeaderInput").should("have.value", secondTipHeader);
    cy.get("@tipsBodyInput").should("have.value", secondTipBody);

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
  });
});
