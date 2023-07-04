import logging
import re


class ANSIfilter:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    filters_ansi = [
        ['\t', '␉'],  # U+2409
        ['\\^\\[\\[\\d*[ABDGJKLMPS]', ''],  # various cursor controls
        ['\\^\\[\\[\\d*C', ' '],  # move cursor forward by \d columns
        ['\\^\\[\\[\\?\\d*c', ''],  # report device {code}?
        ['\\^\\[\\[H', ''],  # move cursor to 1,1
        ['\\^\\[\\[[\\d;]+H', ' '],  # move cursor to next row,col position
        ['\\^\\[\\[[\\d;]*m', ''],  # color codes
        ['\\^\\[\\[\\??[\\d;]*[rhl]', ''],  # set DEC* options (video and cursor)
        ['\\^\\[[=><]', ''],  # '=' enter alt keypad mode, '>' exit alt keypad mode, '<' enter/exit ansi mode
        ['\\^\\[\\[>c', ''],  #
        ['\\^\\[M', ''],
        ['\\^\\[[()][B0]', ''],
        ['\\^\\[\\[K.*', ''],  # Erases from the current cursor position to the end of the current line
        ['.*\\^\\[\\[1K', ''],  # Erases from the current cursor position to the start of the current line
        ['.*\\^\\[\\[2K.*', ''],  # Erases entire current line
        ['\\^\\[\\[\\d*J', ''],  # Erases before/after current line, or whole screen
        ['\\^\\[\\[\\d*@', ''],  # ^[[@
        ['\\^\\[\\[\\d*[d]', ''],  # ^[[<n>d
        ['\\^\\[=', ''],  # ^[=
        ['\\^\\[[\\d;]+', ''],  # ^[[ leftovers
        ['\\^\\[D', ''],  # ^[D, scroll display down one line
        ['\\^D.', ''],  # make ^D erase the character after it
        ['\\^D', ''],  # then if there is a ^D left at the end of the line, delete it too
        ['\\^G', ''],  # delete the bell
        ['.\\^H', ''],  # make ^H erase the character before it
        ['\\^H', ''],  # then if there is a ^H left at the beginning of the line, delete it too
        ['\\^N', ''],  # Shift-Out - select an alternate charset (ever seen "garbage" on your
        ['\\^O', ''],  # TTY when you type?  Use ^O to shift back to your default charset)

        # post ansi cleanups
        ['ESCO[AB]', ''],  # putty/winssh things?
        ['\\^\\[\\]\\d;', ''],  # unidentified, shows up in $PROMPT
        ]

    def filter_ansi(self, input_text):
        """ This function filters things from within the message, replacing
        the match with whatever is listed in the second element
        """
        output_text = ''
        for filtered, replace in self.filters_ansi:
            while True:
                output_text, n_replace = re.subn(filtered, replace, input_text, count=1)
                if not n_replace:
                    break
        return output_text

    def clean_text(self, text):
        text1 = text.split('\n')
        return ''.join(self.filter_ansi(line) for line in text1)

    def clean_file(self, file):
        output_text = ''
        with open(file, 'r') as f:
            x = f.readlines()
            for line in x:
                output_text += self.filter_ansi(line)
        return output_text


# data = '''less +F --follow-name /usr/local/data/CP/log/PersistentFileLogs.txt
# [root@toyota-cu ~]# less +F --follow-name /usr/local/data/CP/log/PersistentFileL
# ogs.txt
# [?1h=
#
# [K0012000300048001000e
#
# [4550] 17/08/2021 07:17:04:185 <CU_CP:UE_CONN_MGR:INFO> RECEIVED_E1AP_BEARER_CON TEXT_RELEASE_COMPLETE:UE_CONN_MGR_GNB_UE_ID=18
# [4551] 17/08/2021 07:17:04:185 <CU_CP:UE_CONN_MGR:SYSTEM> [7mESC[m[33mCP --> AMF [NGA P]: UE CONTEXT RELEASE COMPLETE[7mESC[m[0m
# [4552] 17/08/2021 07:17:04:185 <CU_CP:UE_CONN_MGR:SYSTEM> 2029002a000004000a4003 20a29e0055400200120079400f4002f010010000000002f010000004003c0003000001
#
# [4553] 17/08/2021 07:17:04:185 <CU_CP:RM:INFO> RM_GNB_UE_ID = 18
# [4554] 17/08/2021 07:17:04:185 <2:18:SYSTEM> [7mESC[m[0;0m[7mESC[m[35mipc_client::on_recei ve -> send_msg_to_sctp [7mESC[m[0m
# [4555] 17/08/2021 07:17:04:185 <CU_CP:RM:INFO> RM_GNB_UE_STATE = UE_STATE_UE_REL EASE_ONGOING
# [4556] 17/08/2021 07:17:04:185 <CU_CP:RM:INFO> RM_GNB_UE_EVENT = RM_UE_CONN_RELE ASE_CNF_EVENT
# [4557] 17/08/2021 07:17:04:185 <2:18:SYSTEM> 2029002a000004000a400320a29e0055400 200120079400f4002f010010000000002f010000004003c0003000001
#
# [4558] 17/08/2021 07:17:04:185 <CU_CP:RM:ERROR> UE_ID_NOT_FOUND_IN_CELL_CONTEXT: RM_GNB_UE_ID=18
# [4559] 17/08/2021 07:17:04:185 <CU_CP:RM:ERROR> UE_ID_NOT_FOUND_IN_CELL_CONTEXT: RM_GNB_UE_ID=18
#
# [K[7mWaiting for data... (interrupt to abort)[m
# [K[4560] 17/08/2021 07:19:18:556 <2:1010:INFO> Server running : 6
# [4561] 17/08/2021 07:19:18:556 <2:1010:INFO> Server running EPOLLIN:find 6
# [4562] 17/08/2021 07:19:18:556 <2:1010:INFO> Server running EPOLLIN:nbytes > 0 f d = 6
# [4563] 17/08/2021 07:19:18:556 <2:19:SYSTEM> [7mESC[m[32msctp_protocol_server::on_rec eive[7mESC[m[0m
# [4564] 17/08/2021 07:19:18:556 <2:19:SYSTEM> 000b408152000005002900020013006f000 90002f0100000000010005f00030008df0032000706002af7beb0a8008000812581235c00b001100 aec841061ea08fa13204483d6a0004325981b50201fffffc000001008000007ffffe43b842100044 909b86410004488b08020008018040002c00142140050002662a490838002081840a183d38812285 8c1a3878a1100018034020900d010301b4061304d020601340a1904d030540340e1800d040692341 21f48d05091234162948d060b92341a3348d070e12341e3d48d0810813422504ad92460d2443891a 2b3c51222258006708de19bc4378a6ffc000003002038115aaaa0086000218800f84000e00030101 144007c2000700018100862003e100038200c0c0451001f08001c100614611c5003e100038004150 0300010203a1400540e00c003e1c0000000004000085302811004001015b00500192011918000d88 05901010000
#
# [4565] 17/08/2021 07:19:18:556 <1:1019:INFO> SERVER - Number bytes recv 8.  Firs t Byte = ffffff87
# [4566] 17/08/2021 07:19:18:556 <1:1019:INFO> SERVER - Number bytes recv 391.  Fi rst Byte = 0 '''
#
x = ANSIfilter()
z = x.clean_file(r"C:\Users\rblumberg\PycharmProjects\InfrastructureSVG\InfrastructureSVG\Files_Infrastructure\Log_Analyzer\data\test_logs\initial\CUCP_2021-08-19 11_21_44.log")
# print(z)
# print()
# z = x.clean_text(data)
print(z)
