from InfrastructureSVG.Network_Infrastructure.Send_Outlook_Mail_Infrastructure import SendOutlookMailClass


if __name__ == '__main__':
    send_outlook_mail = SendOutlookMailClass()
    send_outlook_mail.send_outlook_mail(
        server_name='mail.airspan.com',
        username=None,
        password=None,
        sender='Automation_Dev_SVG@airspan.com',
        receives=['azaguri@airspan.com', 'yfarber@airspan.com'],
        subject='SubjectTest',
        text='TextTest'
    )
