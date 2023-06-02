import imaplib
import email.message
import os.path
import datetime
import base64
import re


pause_time = 5000


class Getmail():
    """ClientTask"""
    def __init__(self):
        self.id = 1

    def yandex(self,sender):
        YA_HOST = "imap.yandex.ru"
        YA_PORT = 993
        YA_USER = "lapithome"
        YA_PASSWORD = "nisargadatta13"

        filelist = []
        sender = sender[:re.search('@', sender).end()-1]
        print(sender)
        # подключились к почте и логинемся
        imap = imaplib.IMAP4_SSL(YA_HOST)
        imap.login(YA_USER, YA_PASSWORD)
        status, select_data = imap.select()
        # nmessages = select_data[0].decode('utf-8')

        # от кого письмо
        status, search_data = imap.search(None, 'FROM', sender)
        for msg_id in reversed(search_data[0].split()):
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
        # включает в себя заголовки и альтернативные полезные нагрузки
            mail = email.message_from_bytes(msg_data[0][1])

            if mail.is_multipart():
                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                        continue

                    content_type = part.get_content_type()
                    filename = part.get_filename()

                    transfer_encoding = part.get_all('Content-Transfer-Encoding')
                    if transfer_encoding and transfer_encoding[0] == 'base64':
                        filename_parts = filename.split('?')
                        filename = base64.b64decode(filename_parts[3]).decode(filename_parts[1])

                    if filename:
                        if '.xls' and 'ремни' in filename.lower():
                            filelist.append(filename)
                            print('Закачали файл: ', filename)
                            # Нам плохого не надо, в письме может быть всякое барахло
                            with open(filename, 'wb') as new_file:
                                new_file.write(part.get_payload(decode=True))
                break
        imap.expunge()
        imap.logout()
        return filelist


    def gmail(self,sender):
        # https://support.google.com/accounts/answer/6010255?hl=ru
        YA_HOST = "imap.gmail.com"
        YA_PORT = 993
        YA_USER = "lapithome@gmail.com"
        YA_PASSWORD = "nisargadatta13"

        filelist = []
        sender = sender[:re.search('@', sender).end()-1]
        print(sender)
        # подключились к почте и логинемся

        imap = imaplib.IMAP4_SSL(YA_HOST,YA_PORT)
        imap.login(YA_USER, YA_PASSWORD)
        status, select_data = imap.select()
        # nmessages = select_data[0].decode('utf-8')

        # от кого письмо
        status, search_data = imap.search(None, 'FROM', sender)
        for msg_id in reversed(search_data[0].split()):
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
        # включает в себя заголовки и альтернативные полезные нагрузки
            mail = email.message_from_bytes(msg_data[0][1])

            if mail.is_multipart():
                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                        continue

                    content_type = part.get_content_type()
                    filename = part.get_filename()

                    transfer_encoding = part.get_all('Content-Transfer-Encoding')
                    if transfer_encoding and transfer_encoding[0] == 'base64':
                        filename_parts = filename.split('?')
                        filename = base64.b64decode(filename_parts[3]).decode(filename_parts[1])

                    if filename:
                        if '.xls' and 'ремни' in filename.lower():
                            filelist.append(filename)
                            print('Закачали файл: ', filename)
                            # Нам плохого не надо, в письме может быть всякое барахло
                            with open(filename, 'wb') as new_file:
                                new_file.write(part.get_payload(decode=True))
                break
        imap.expunge()
        imap.logout()
        return filelist



