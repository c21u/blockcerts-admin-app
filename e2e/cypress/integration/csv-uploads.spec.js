describe("CSV Uploads", () => {
  context("Invite view CSV upload custom command", () => {
    const INVITE_CSV_UPLOAD = "inviteCsvUpload";
    Cypress.Commands.add(INVITE_CSV_UPLOAD, fixtureName => {
      const instanceId = "1";
      cy.visit(`/manage_recipients/${instanceId}/invite`);
      cy.get("h1[data-test-id=app-credential-invite-title]")
        .should("exist")
        .should("contain", "Manage Recipients - Invite");

      // Call the CSV Upload custom command from cypress/support/commands
      cy.csvUpload(fixtureName);

      cy.get("button[data-test-id=app-invite-submit-button]").click();

      // expect successful submit to redirect to Manage Recipients - Approve view
      cy.get("h1[data-test-id=app-credential-approve-title]")
        .should("exist")
        .should("contain", "Manage Recipients - Approve");
    });
  });

  before(() => {
    // log in only once before any of the tests run.
    cy.login();
  });

  // NB: this test is gonna be flaky since it relies on a seeded fixture with ID=1
  it("Should upload CSV with first_name,last_name,email", () => {
    cy.inviteCsvUpload("example.csv");
  });

  it("Should not blow up when a CSV with BOM is uploaded", () => {
    cy.inviteCsvUpload("bom.csv");
  });
});
