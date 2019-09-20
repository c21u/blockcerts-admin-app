const casServerUrl = Cypress.env("CAS_SERVER_URL");

Cypress.Commands.add("login", () => {
  cy.request(casServerUrl).then(response => {
    const parser = new DOMParser();
    const html = parser.parseFromString(response.body, "text/html");
    const inputElement = html.querySelector("input[name='execution']");
    expect(inputElement).to.not.be.null;
    cy.request({
      method: "POST",
      url: casServerUrl,
      form: true,
      body: {
        execution: inputElement["value"],
        username: Cypress.env("CAS_USERNAME"),
        password: Cypress.env("CAS_PASSWORD"),
        _eventId: "submit"
      }
    });
  });
});
