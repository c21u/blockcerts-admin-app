const casServerUrl = Cypress.env("CAS_SERVER_URL");

Cypress.Commands.add("login", () => {
  cy.request(casServerUrl).then(response => {
    expect(response.status).to.eql(200);

    const parser = new DOMParser();
    const html = parser.parseFromString(response.body, "text/html");
    const loginForm = html.querySelector("form#fm1");
    if (loginForm === null) {
      // form#fm1 is the CAS demo app login form, if we didn't find it,
      // then assume we are logged in already.
      cy.log("Skipping CAS login form.");
    } else {
      cy.log("Found CAS login form.");
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
    }
  });
});
