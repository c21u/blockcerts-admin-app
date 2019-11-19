# blockcerts-admin-app
A web interface for creating and issuing blockcerts

![Build status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiVHI0MHR1UWR5MktsZ2pMcUJqemU1L0FFM0U2ZjlXcXQwSUJvcFUvRkh5S1JnRGVlSnJWbllEckx3NmdrNnoxUHNHZldFV2ordStEOWRmQzYxNE5tN3pZPSIsIml2UGFyYW1ldGVyU3BlYyI6IkJqSzRlbDlXcmZvOWhOZmwiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

This is a Django based web-app that ties together the functionalities of cert-tools, cert-issuer, and cert-mailer into an interface suitable for non-technical users to author certificates and manage rosters for issuing them.

To set up a local dev instance, first generate SSL certs using mkcert, install it with the instructions at https://github.com/FiloSottile/mkcert and generate certs by running:

    mkcert -install
    mkdir -p ~/certs
    mkcert -cert-file ~/certs/127.0.0.1.xip.io.crt -key-file ~/certs/127.0.0.1.xip.io.key '*.127.0.0.1.xip.io'

Now you can build and start the server with `docker-compose up --build` and populate it with some fake data by running `docker exec blockcerts-admin-app_web_1 python3 manage.py seed` then visit https://admin.127.0.0.1.xip.io in your browser.

The test CAS server that the dev instance connects to will accept username: `casuser` password: `Mellon` 
