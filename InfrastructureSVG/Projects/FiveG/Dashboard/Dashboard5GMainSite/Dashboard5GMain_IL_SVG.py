from InfrastructureSVG.Projects.FiveG.Dashboard.Dashboard5GMainFunction import main
from InfrastructureSVG.Projects.FiveG.Dashboard.DashboardPerGorupName.DashboardStructure import \
    TesterDashboard, ExecutiveDashboard


DASHBOARD_CLASS = [
    TesterDashboard,
    ExecutiveDashboard,
]

PROJECT_NAME = 'Dashboard-5G'
SITE = ' IL SVG'

if __name__ == '__main__':
    main(PROJECT_NAME, SITE, DASHBOARD_CLASS)
