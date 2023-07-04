import logging
import PyPDF2
import re

from InfrastructureSVG.Projects.General.TenableScanAndReport.TenableDefect import OpenOrUpdateDefect
from InfrastructureSVG.Tenable_Infrastructure.Tenable import ExtractDetailsFromWeb


class ExtractPDFDetails:
    def __init__(self, pdf_path, _key_terms=r"Plugin Id", _severity=None):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

        if _severity:
            self.severity = _severity
        else:
            self.severity = ['Critical', 'High', 'Medium', 'Low', 'Info']

        self.pdf_path = pdf_path
        self.pdf_object = None
        self.key_terms = _key_terms
        self.full_page_number = 0

        self.tenable_details_dict = {}

    def open_the_pdf_file(self):
        return PyPDF2.PdfFileReader(self.pdf_path)

    def get_number_of_pages(self):
        self.full_page_number = self.pdf_object.getNumPages()

    def find_page_number_of_details(self):
        for page_number in range(self.full_page_number):
            page_obj = self.pdf_object.getPage(page_number)
            text = page_obj.extractText()
            res_search = re.search(self.key_terms, text)
            if res_search:
                return page_number

    def extract_text(self, from_page_number):
        text = ''
        for page_number in range(from_page_number, self.full_page_number):
            page_obj = self.pdf_object.getPage(page_number)
            text += page_obj.extractText()

        text_list = text.split('Details\nSeverity\nPlugin Id\nName')
        return text_list[1]

    def fill_tenable_details_dict(self, text, from_page_number):
        count = 0
        details_list = []
        index = 0
        for value in list(filter(None, text.split('\n'))):
            if value.isdigit() and self.full_page_number >= int(value) >= from_page_number:
                continue
            if count == 3:
                if details_list[0] not in self.severity:
                    continue

                self.tenable_details_dict.update(
                    {
                        index: {
                            'Severity': details_list[0],
                            'Plugin Id': f'{details_list[1]}',
                            'Name': f'{details_list[2]}'
                        }
                    }
                )
                count = 0
                details_list = []
                index += 1
            details_list.append(value)
            count += 1

    def process(self):
        self.pdf_object = self.open_the_pdf_file()
        self.get_number_of_pages()

        # extract text and do the search
        from_page_number = self.find_page_number_of_details()
        text = self.extract_text(from_page_number)
        self.fill_tenable_details_dict(text, from_page_number)


if __name__ == '__main__':
    node_name = 'Aviz'
    site = 'IL SVG'

    entity_version = ''
    entity_type = ''
    bs_hw_type = ''
    ip_address = ''
    defect_parameters_dict = {
        'entity_version': entity_version,
        'entity_type': entity_type,
        'bs_hw_type': bs_hw_type,
        'test_environments': ip_address,
    }

    pdf_path_ = '\\\\192.168.127.247\\TenableScans\\2022_02_22\\SecurityScan_ AvizTest_22_9_bs_hw_type_1_entity_version_12345_kernel_version_12345.pdf'
    extract_pdf_details = ExtractPDFDetails(pdf_path=pdf_path_)
    extract_pdf_details.process()

    # open defect
    defects_dict = {'new_defects_list': [], 'existing_defects_list': []}
    for k, v in extract_pdf_details.tenable_details_dict.items():
        plugin_name = v['Name']
        plugin_id = v['Plugin Id']
        severity_name = v['Severity']
        if severity_name not in extract_pdf_details.severity:
            continue

        extract_details_from_web_output = ExtractDetailsFromWeb()
        extract_details_from_web_output.process(node_name=node_name, severity_name=severity_name, plugin_id=plugin_id, plugin_name=plugin_name)
        description = f'URL: https://www.tenable.com/plugins/nessus/{plugin_id}\n{extract_details_from_web_output.output}'

        print()
        # open defect
        open_defect = OpenOrUpdateDefect(
            summary=plugin_name,
            label=plugin_id,
            site=site,
            severity=severity_name,
            description=description,
            folder_path=pdf_path_,
            defect_parameters_dict=defect_parameters_dict
        )
        defect = open_defect.found_or_create_defect()
        defects_dict[f'{list(defect.keys())[0]}s_list'].append(defect.get(list(defect.keys())[0]))
