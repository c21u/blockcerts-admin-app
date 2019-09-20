const casServerUrl = "https://casserver.herokuapp.com/cas/login";

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
        username: "casuser",
        password: "Mellon",
        _eventId: "submit"
      }
    });
  });
});
