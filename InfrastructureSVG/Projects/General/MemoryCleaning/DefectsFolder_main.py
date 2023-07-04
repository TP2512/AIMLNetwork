from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Projects.General.MemoryCleaning.DeleteCloseDefects import DeletePerCloseDefect


if __name__ == '__main__':
    project_name, site = 'Delete Old Close Defect Folders', 'IL SVG'

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    close_defects = DeletePerCloseDefect()
    close_defects.delete_defects_from_defects_folder(debug=True)
