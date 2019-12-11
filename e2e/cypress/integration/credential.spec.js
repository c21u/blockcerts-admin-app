describe("Credential", () => {
  context("Create Credential custom command", () => {
    const CREATE_CREDENTIAL = "createCredential";
    Cypress.Commands.add(CREATE_CREDENTIAL, fixtureName => {
      cy.visit("/add_credential");
      cy.get("#id_title").type("Underwater Basketweaving 101");
      cy.get("#id_description").type("Intro to Underwater Basketweaving");
      cy.get("#id_narrative").type("Demonstrated ability to weave a basket underwater.");
      cy.get("#id_issuing_department").select("1");
      cy.get("#id_cert_mailer_config").select("1");
      cy.get("#id_cert_tools_config").select("1");

      cy.get(".btn-primary").click();

      // expect successful submit to redirect to same page with empty fields
      cy.location('href').should('include', '/add_credential')
      cy.get("#id_title").invoke('val').should('eq', '');
      cy.get("#id_description").invoke('val').should('eq', '');
      cy.get("#id_narrative").invoke('val').should('eq', '');
      cy.get("#id_issuing_department").invoke('val').should('eq', 'C21U');

    });
  });

  before(() => {
    // log in only once before any of the tests run.
    cy.login();
  });

  // NB: this test is gonna be flaky since it relies on a seeded fixture with ID=1
  it("Should create a credential", () => {
    cy.createCredential();
  });
});
