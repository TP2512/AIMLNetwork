class Credentials:
    def __init__(self):
        pass

    @staticmethod
    def credentials_per_app(app):
        user = ''
        password = ''
        if app == 'Dashboard':  # Jira
            user = 'Dashboard_SVG'
            password = 'N24M6cUn'

        elif app == 'Nessus':  # Jira
            user = 'Nessus_SVG'
            password = 'eMMy4w4z'

        elif app == 'EZlife':  # Jira
            user = 'EZlife_SVG'
            password = 'dDf9R953'

        elif app == 'Automation_Dev':  # Jira
            user = 'Automation_Dev_SVG'
            password = '6G7vaErz'

        elif app == 'SwEnginetime':  # Jira
            user = 'EngineTime'
            password = 'gD9z*R$5'

        elif app == 'TestspanAuto':  # Jira
            user = 'TestspanAuto'
            password = 'air_auto1'

        elif app == 'CoreCare':  # Jira
            user = 'CoreCare'
            password = 'Zgya3$N6'

        elif app == 'CoreCare-5G':  # Jira
            user = 'CoreCare-5G'
            password = 'U63brLAj'

        elif app == 'elasticsearch_production':  # Elastic
            user = 'elastic'
            password = 'auto_dev9'

        elif app == 'elasticsearch_dev':  # Elastic
            user = 'elastic'
            password = 'sp_user9'

        elif app == 'jenkins':  # Jenkins
            user = 'azaguri@airspan.com'
            password = '11d56ce3b96e9cbc784a062bc10eecad35'

        elif app == 'spuser':  # Old Domain
            user = 'spuser'
            password = 'sp_user9'

        elif app == 'spuser_domain':  # Domain
            user = 'spuser@airspan.com'
            password = 'sp_user9'

        return user, password
