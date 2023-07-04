import logging


class CalculateTime:
    def __init__(self, h: str, m: str, s: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.d = None
        self.h = int(h)
        self.m = int(m)
        self.s = int(s)

    def calculate_time(self):
        self.m = self.m + (self.s // 60)
        self.s = self.s % 60

        self.h = self.h + (self.m // 60)
        self.m = self.m % 60

        self.d = self.h // 24
        self.h = self.h % 24

    def calculate_minutes(self):
        self.calculate_time()
        return int(self.m + (self.d * 24 * 60) + (self.h * 60) + (self.s / 60))

    def put_result(self):
        self.logger.info(f"{self.d} Days, {self.h} Hours, {self.m} Minutes, {self.s} Seconds")
        print(f"{self.d} Days, {self.h} Hours, {self.m} Minutes, {self.s} Seconds")


if __name__ == '__main__':
    print("The total time elapsed is ", end=" ")
    T1 = CalculateTime(h='25', m='61', s='61')
    print(T1.calculate_minutes())
    print()
    T1.calculate_time()
    T1.calculate_minutes()
    T1.put_result()
    print()
