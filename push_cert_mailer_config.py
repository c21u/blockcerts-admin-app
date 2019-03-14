import os
import configargparse
import json

import django


def push_cert_mailer_config():
    cwd = os.getcwd()
    config_file_path = os.path.join(cwd, 'conf_mailer.ini')
    p = configargparse.getArgumentParser(default_config_files=[config_file_path])

    # p.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')

    p.add_argument('--from_email', required=True, type=str, help='from email address')
    p.add_argument('--distribution_list', required=True, type=str, help='csv file with emails and substitutions')
    p.add_argument('--introduction_url', required=True, type=str, help='url for introducing the wallet to the issuer')
    p.add_argument('--introduction_email_subject', required=True, type=str, help='subject of the email')
    p.add_argument('--introduction_email_body', required=True, type=str, help='body of the email')
    p.add_argument('--mailer', required=True, type=str, help='the mail api to use')

    args, _ = p.parse_known_args()
    args_s = json.dumps(args.__dict__)
    _ = CertMailerConfig.objects.all().delete()
    _, created = CertMailerConfig.objects.get_or_create(
        config=args_s
    )


if __name__ == '__main__':
    print("Pushing cert mailer config...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
    django.setup()
    from issuer.models import CertMailerConfig
    push_cert_mailer_config()