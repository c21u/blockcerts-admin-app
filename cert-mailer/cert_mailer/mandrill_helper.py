import mandrill
import os

mandrill_client = mandrill.Mandrill(os.environ.get('MANDRILL_API_KEY'))


def send(config, subject, body, img, row):
    message = {
        'from_email': config.from_email,
        'subject': subject,
        'html': body,
        'auto_text': True,
        'images': [
            {
                'type': 'image/jpeg',
                'name': 'qrcode',
                'content': img
            }
        ],
        'to': [{'email': row['email']}]
    }
    try:
        result = mandrill_client.messages.send(message=message, async=False)
    except mandrill.Error as e:
        print('A mandrill error occurred: %s - %s' % (e.__class__, e))
        exit()

    print(result)
