describe("CSV Uploads", () => {
  before(() => {
    // log in only once before any of the tests run.
    cy.login();
  });

  // NB: this test is gonna be flaky since it relies on a seeded fixture with ID=1
  it("Should upload CSV with first_name,last_name,email", () => {
    cy.visit("/manage_recipients/1/invite");
    cy.get("h1[data-test-id=app-credential-invite-title]")
      .should("exist")
      .should("contain", "Manage Recipients - Invite");

    const fileName = "example.csv";
    cy.fixture(fileName).then(fileContent => {
      console.dir(fileContent);
      cy.get("#csv_file").upload({
        fileContent,
        fileName: fileName,
        mimeType: "text/csv"
      });
    });

    cy.get("button[data-test-id=app-invite-submit-button]").click();

    // expect successful submit to redirect to Manage Recipients - Approve view
    cy.get("h1[data-test-id=app-credential-approve-title]")
      .should("exist")
      .should("contain", "Manage Recipients - Approve");
  });

  it("Should not blow up when a CSV with BOM is uploaded", () => {
    cy.visit("/manage_recipients/1/invite");
    cy.get("h1[data-test-id=app-credential-invite-title]")
      .should("exist")
      .should("contain", "Manage Recipients - Invite");

    const fileName = "another.csv";
    cy.fixture(fileName).then(fileContent => {
      console.dir(fileContent);
      cy.get("#csv_file").upload({
        fileContent,
        fileName: fileName,
        mimeType: "text/csv"
      });
    });

    cy.get("button[data-test-id=app-invite-submit-button]").click();

    // expect successful submit to redirect to Manage Recipients - Approve view
    cy.get("h1[data-test-id=app-credential-approve-title]")
      .should("exist")
      .should("contain", "Manage Recipients - Approve");
  })
});
