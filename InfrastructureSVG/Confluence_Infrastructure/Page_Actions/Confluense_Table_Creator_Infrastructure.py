import logging


"""
In this py file have 1 class
    - ConfluenceHtmlCreatorClass
"""


class ConfluenceHtmlCreatorClass:
    """ This class ("ConfluenceHtmlCreatorClass") responsible for creating Confluence Html table page """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def create_table_page(self, title_list, row_list, color_cell, row_list_of_list=False):
        """
        This function responsible Create "confluence Html title" as part of confluence page

        The function get 2 parameter:
            - "confluence" - client of confluence (real)
            - "title_list" - parameter need to be the title of the table (list type)
                * for example: [IP, Vendor, etc..]
            - "row_list" - parameter need to be one row from the table (from the full row list) of the table (list type)
            - "color_cell" - parameter need to be the title of the table (string type)

        The function return 1 parameters:
            - "full_html_page" - The full html page of the confluence page (string type)
        """

        title_header = ConfluenceHtmlCreatorClass().confluence_html_title(title_list)
        # if row_list_of_list:
        #     for row_list_ in row_list:
        #         table_header_ = ConfluenceHtmlCreatorClass.create_one_row_in_table(row_list_, color_cell,
        #                                                                            row_list_of_list)
        #         table_header.append(table_header_)
        #     else:
        #         table_header_ = ConfluenceHtmlCreatorClass.create_one_row_in_table(row_list, color_cell,
        #                                                                            row_list_of_list)
        #         table_header.append(table_header_)

        table_header = ConfluenceHtmlCreatorClass().create_one_row_in_table(row_list, color_cell, row_list_of_list)

        return ConfluenceHtmlCreatorClass().row_assembly(title_header, table_header)

    def confluence_html_title(self, title_list):
        """
        This function responsible Create "confluence Html title" as part of confluence page

        The function get 2 parameter:
            - "title_list" - parameter need to be the title of the table (list type)
                * for example: [IP, Vendor, etc..]

        The function return 1 parameters:
            - "title_header" - The full title header as part of the confluence page (string type)
        """

        try:
            title_header_1 = "<p></p>" \
                             "<table class=\"wrapped\">" \
                             "<colgroup>" \
                             "<col />" \
                             "<col />" \
                             "<col />" \
                             "</colgroup>" \
                             "<tbody>" \
                             "<tr>" \
                             ""

            title_header_2 = ''
            for title in title_list:
                title_header_2 = f"{title_header_2}<th>{title}</th>"
            return title_header_1 + title_header_2 + "</tr>"
        except Exception:
            self.logger.exception('')
            return None

    def create_one_row_in_table(self, row_list, color_cell, row_list_of_list=False):
        """
        This function responsible Create "confluence Html rows" as part of confluence page

        The function get 2 parameter:
            - "row_list" - parameter need to be one row from the table (from the full row list) of the table (list type)
            - "color_cell" - parameter need to be the title of the table (string type)

        The function return 1 parameters:
            - "full_row" - The full rows as part of the confluence page (string type)
        """

        full_row = ''
        try:
            if row_list_of_list:
                full_row = []
                for row_one_list in row_list:
                    row = ''
                    for row_ in row_one_list:
                        row = row + ("<td class=\"highlight-" + color_cell + "\" data-highlight-colour=\"" +
                                     color_cell + "\">" + str(row_) + "</td>")
                    row = f"<tr>{row}</tr>"
                    full_row.append(row)
            else:
                row = ''
                for row_ in row_list:
                    row = row + ("<td class=\"highlight-" + color_cell + "\" data-highlight-colour=\"" + color_cell +
                                 "\">" + str(row_) + "</td>")
                    full_row = f"<tr>{row}</tr>"

            return full_row
        except Exception:
            self.logger.exception('')
            return None

    def row_assembly(self, title_header, table_header):
        """
        This function responsible Create "confluence Html" as part of confluence page

        The function get 2 parameter:
            - "title_header" - parameter need to be the title header as part of the confluence page (string type)
            - "color_cell" - parameter need to be the color cell as part of the confluence page (string type)

        The function return 1 parameters:
            - "full_html_page" - The full html page of the confluence page (string type)
        """

        try:
            end_of_html = "</tbody>" \
                          "</table>" \
                          "<p class=\"auto-cursor-target\">" \
                          "<br />" \
                          "</p>"

            html_table = ''.join(table_header)
            return title_header + html_table + end_of_html
        except Exception:
            self.logger.exception('')
            return None
