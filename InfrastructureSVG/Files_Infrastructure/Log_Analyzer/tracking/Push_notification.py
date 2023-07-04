import http.client
from urllib import parse


class Notifications:
    def __init__(self, recipient):
        if recipient == 'rblumberg':
            self.token = 'ah4atom643mkjkjazaby3ap381c58e'
            self.user = 'u17nne2c6c4yfh98sorq8hdvxcut3x'

    # send push notification to developer phone
    def notify(self, message_title, message):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     parse.urlencode({
                         "token": self.token,
                         "user": self.user,
                         "title": message_title,
                         "message": message,
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()

    # send push notification to developer phone from commandline (for envirnonment creation script)
    # def notify_from_cmd(self, args):
    #     conn = http.client.HTTPSConnection("api.pushover.net:443")
    #     conn.request("POST", "/1/messages.json",
    #                  urllib.parse.urlencode({
    #                     "token": "ah4atom643mkjkjazaby3ap381c58e",
    #                     "user": "u17nne2c6c4yfh98sorq8hdvxcut3x",
    #                     "title": args['message_title'],
    #                     "message": args['message'] + " \ntime taken:" + args['elapsed'],
    #                     }), {"Content-type": "application/x-www-form-urlencoded"})
    #     conn.getresponse()

# run send push from command line with arguments
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-t','--message_title', help='message title', required=True)
#     parser.add_argument('-m', '--message', help='message content', required=True)
#     parser.add_argument('-e', '--elapsed', help='elapsed time', required=True)
#     args = vars(parser.parse_args())
#     recipient = 'rblumberg'
#     notifications = Notifications(recipient)
#     notifications.notify_from_cmd(args=args)
