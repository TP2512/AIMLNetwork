from jira import JIRA, JIRAError
from datetime import datetime

if __name__ == '__main__':
    data = ''
    total_data = ''
    try:
        server = 'https://helpdesk.airspan.com'
        username = input('please enter your jira username: ')
        password = input('please enter your jira password: ')
        def_customer_name = input('please enter your "Customer Name" (as written in Jira on DEF project): ')
        days = input('Please enter a few days (back) to search: ')
        print('Start CoreCount process, It will take several moments')

        jira_client = JIRA(basic_auth=(username, password), options={'server': server}, timeout=580)

        defect_filter = f'project = "Defect Tracking" AND ' \
                        f'issueFunction in linkedIssuesOf("project = corecare") AND ' \
                        f'"Test Environments" = Customer_Tier3_{def_customer_name.replace(" ", "_")} AND ' \
                        f'reporter in (CoreCare-5G) AND ' \
                        f'status in ' \
                        f'(Parked, Pending, Processing, "To Reproduce", "Ready for Verification", "Fixed in R&D", "Assigned to 3rd Party", "Need more Info", "Duplicate") AND ' \
                        f'updated >= -{days}d'
        print(f'defect_filter is: {defect_filter}')

        defects = jira_client.search_issues(defect_filter, maxResults=5000)
        defects_list = [defect.key for defect in defects.iterable]
        total_data += f'Defects count is: {len(defects_list)}\n'
        total_data += f'Defects list is: {defects_list}\n\n\n'

        try:
            for defect in defects:
                data = f'### Defect: {defect.key} ###\n'
                epics = jira_client.search_issues(
                    f'project = "CoreCare" AND '
                    f'issuetype = Epic AND '
                    f'issue in linkedissues({defect.key})',
                    maxResults=5000
                )
                cores_list = []
                for epic in epics:
                    cores_filter = f'project = CoreCare AND ' \
                                   f'issuetype = Core AND ' \
                                   f'"Epic Link" = {epic.key} AND ' \
                                   f'"Test Environments" = Customer_Tier3_{def_customer_name.replace(" ", "_")} AND ' \
                                   f'reporter in (CoreCare-5G) AND ' \
                                   f'updated >= -{days}d'
                    print(f'cores_filter is: {cores_filter}')

                    cores = jira_client.search_issues(cores_filter, maxResults=5000)
                    cores_list = [core.key for core in cores]
                data += f'Cores count is: {len(cores_list)}\n'
                data += f'Cores list is: {cores_list}\n'

                data += '\n\n'
                total_data += data
                print()
        except JIRAError as jira_error:
            data = f'jira_error is: {jira_error}\n\n\n'
            total_data += data
        except Exception as error:
            data = f'error is: {error}\n\n\n'
            total_data += data

    except JIRAError as jira_error:
        total_data += f'\n\njira_error is: {jira_error}\n'
    except Exception as error:
        total_data += f'\n\nerror is: {error}\n'
    finally:
        date_and_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
        with open(f'CoreCount {date_and_time}.txt', 'w') as f:
            f.write(total_data)
