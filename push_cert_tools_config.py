import os
import configargparse
import json

import django

from cert_tools import helpers

def push_cert_tools_config():
    cwd = os.getcwd()
    config_file_path = os.path.join(cwd, 'conf_cert_tools.ini')
    p = configargparse.getArgumentParser(default_config_files=[config_file_path])

    # p.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')

    # p = configargparse.getArgumentParser(default_config_files=[os.path.join(cwd, 'conf.ini')])
    p.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    p.add_argument('--data_dir', type=str, help='where data files are located')
    p.add_argument('--issuer_logo_file', type=str, help='issuer logo image file, png format')
    p.add_argument('--cert_image_file', type=str, help='issuer logo image file, png format')
    p.add_argument('--issuer_url', type=str, help='issuer URL')
    p.add_argument('--issuer_certs_url', type=str, help='issuer certificates URL')
    p.add_argument('--issuer_email', required=True, type=str, help='issuer email')
    p.add_argument('--issuer_name', required=True, type=str, help='issuer name')
    p.add_argument('--issuer_id', required=True, type=str, help='issuer profile')
    p.add_argument('--issuer_key', type=str, help='issuer issuing key')
    p.add_argument('--certificate_description', type=str, help='the display description of the certificate')
    p.add_argument('--certificate_title', required=True, type=str, help='the title of the certificate')
    p.add_argument('--criteria_narrative', required=True, type=str, help='criteria narrative')
    p.add_argument('--template_dir', type=str, help='the template output directory')
    p.add_argument('--template_file_name', type=str, help='the template file name')
    p.add_argument('--hash_emails', action='store_true',
                   help='whether to hash emails in the certificate')
    p.add_argument('--revocation_list', type=str, help='issuer revocation list')
    p.add_argument('--issuer_public_key', type=str, help='issuer public key')
    p.add_argument('--badge_id', required=True, type=str, help='badge id')
    p.add_argument('--issuer_signature_lines', action=helpers.make_action('issuer_signature_lines'),
                   help='issuer signature lines')
    p.add_argument('--additional_global_fields', action=helpers.make_action('global_fields'),
                   help='additional global fields')
    p.add_argument('--additional_per_recipient_fields', action=helpers.make_action('per_recipient_fields'),
                   help='additional per-recipient fields')
    p.add_argument('--display_html', type=str, help='html content to display')
    args, _ = p.parse_known_args()
    args.abs_data_dir = os.path.abspath(os.path.join(cwd, args.data_dir))

    args, _ = p.parse_known_args()
    print(args.additional_global_fields)
    args.abs_data_dir = os.path.abspath(os.path.join(cwd, args.data_dir))
    args_s = json.dumps(args.__dict__)
    _ = CertToolsConfig.objects.all().delete()
    _, created = CertToolsConfig.objects.get_or_create(
        config=args_s
    )


if __name__ == '__main__':
    print("Pushing cert mailer config...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
    django.setup()
    from issuer.models import CertToolsConfig
    push_cert_tools_config()