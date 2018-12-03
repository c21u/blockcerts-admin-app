Cert-Mailer
===========

This is a tool to send emails to your certificate recipients.

To use it, set up an account at sendgrid.com and add your API key to your environment:

    export SENDGRID_API_KEY='SG.123ABC'

Copy `conf.sample.ini` to `conf.ini` and edit it to include your issuer's `intruduction_url` and `cert_url` the `{}` will be replaced with the cert filename from the distribution list.
The `introduction_email_body` is a template where any `$key` will be replaced by `key` from the distribution list, `$introduction_url` and `$qrcode` can also be used.
The `cert_email_body` works the same way but has `$cert_url` instead of `$introduction_url`.

Set up a venv:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Now you can send your issuer introduction emails:

    python introduce.py

And your cert issuance emails:

    python sendcert.py
