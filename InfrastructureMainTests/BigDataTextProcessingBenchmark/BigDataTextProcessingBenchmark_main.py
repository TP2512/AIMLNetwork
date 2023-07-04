from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from InfrastructureMainTests.BigDataTextProcessingBenchmark.BigDataTextProcessingBenchmark import BigDataTextProcessingBenchmark
from datetime import datetime, timezone


PROJECT_NAME = 'Big Data Text Processing Benchmark'

ACTIVE_DATE_TIME = datetime.now(timezone.utc)
DATE_STRING = ACTIVE_DATE_TIME.strftime("%Y.%m.%d")
TIME_STRING = ACTIVE_DATE_TIME.strftime("%H.%M")
SITE = 'IL SVG'


def build_logger(site: str):
    log_file_name = f'{DATE_STRING}_{TIME_STRING} - {PROJECT_NAME.replace(" ", "_")}_Logs_{site.replace(" ", "_")}'
    log_path = f'C:\\Python Logs\\{PROJECT_NAME}\\{site}'
    return ProjectsLogging(project_name=PROJECT_NAME, path=log_path, file_name=log_file_name).project_logging(timestamp=True)

if __name__ == "__main__":
    print(f'Start {PROJECT_NAME}')
    logger = build_logger(site=SITE)
    try:
        bigDataTextProcessingBenchmark = BigDataTextProcessingBenchmark()
        bigDataTextProcessingBenchmark.run_benchmark()
    except Exception:
        logger.exception('Main function exception')
