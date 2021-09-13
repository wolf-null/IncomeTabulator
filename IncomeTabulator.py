import json
import csv
import calendar
import datetime as dt
import sys
from datetime import datetime

from Errors import ErrorNoValue


def pick_workdays(start, border, workdays : list, days_in_month : list, month : int):
    """
    Returns the workdays belong to this interval, started at selected <month>
    Month indexing starts with 0. Day indexing is ordinary (with 1)
    :param workdays: List of lists with workdays
    :param days_in_month: List of days in month.
    :param month: Month from which to pick workdays
    :return: (<list>, <list>). workdays in this <month> inside this interval, workday in the next <month> inside this interval
    """

    cycling = start > border
    possible_days_this_month = range(start, days_in_month[month] + 1 if cycling else border)
    possible_days_next_month = range(1, border if cycling else 1)

    # Possible issue!

    days_this_month = list(filter(lambda x: x in workdays[month], possible_days_this_month))
    if month != 11:
        days_next_month = list(filter(lambda x: x in workdays[month + 1], possible_days_next_month))
    else:
        days_next_month = list()

    return days_this_month, days_next_month


def pick_payday(start, payday, workdays : list, days_in_month : list, month : int):
    """
    For parameters see pick_workdays()
    :return: payday : int, next_month : boolean.
    """
    days_this_month, days_next_month = pick_workdays(start, payday, workdays, days_in_month, month)
    if len(days_next_month) > 0:
        return max(days_next_month), True
    else:
        return max(days_this_month), False


if __name__ == '__main__':
    input_fname = 'input.json'
    output_fname = 'output.csv'

    if len(sys.argv) > 1:
        input_fname = sys.argv[1]
    if len(sys.argv) == 2:
        output_fname = sys.argv[2]

    with open(input_fname, 'r') as input_file:
        data = json.load(input_file)

    # ----------------- Input read and error check -----------------

    # Advance and balance intervals and paydays
    try:
        interval_1 = range(data['advance-starts-from'], data['balance-starts-from'])
        day_advance, day_balance = data['advance-payday'], data['balance-payday']
    except ValueError:
        print('Problems with configuration file! Using default values\nadvance-starts-from: 1\nbalance-starts-from: '
              '16\nadvance-payday: 20\nbalance-payday: 5\n')
        interval_1 = range(1, 16)
        day_advance, day_balance = 20, 5

    # The year
    year = data['year'] if 'year' in data else dt.date.today().year

    # Regular salary
    if 'salary' not in data:
        raise ErrorNoValue('salary key is missing')
    try:
        salary = float(data['salary'])
    except ValueError:
        print("[ERROR]: salary value should be a floating point like 300000.1 without measuring units")
        raise

    # Bonus payment
    if 'bonus' in data:
        try:
            bonus = float(data['bonus'])
        except ValueError:
            print("[ERROR]: bonus value should be a floating point like 300000.1 without measuring units")
            raise
    else:
        bonus = 0
        print('bonus value is not specified in the input. Assuming bonus=0')

    # Taxes
    if 'tax' in data:
        try:
            tax = float(data['tax'])
            if not(0 <= tax < 1):
                raise ValueError('[ERROR]: Tax should fit condition 0 <= tax < 1 (normalized by 1)')
        except ValueError:
            raise ValueError('[ERROR]: tax value should be a floating point value like 0.13')
    else:
        tax = 0

    # Alignment method
    if 'csv-delimiter' in data:
        delimiter = data['csv-delimiter']
    else:
        delimiter = ';'  # MS Excel fucking standard. Won't read tabs and commas.

    # Days in month
    days_in_month = [calendar.monthrange(year, month)[1] for month in range(1, 13)]

    # Workdays
    work_days = [list() for m in range(1, 13)]
    try:
        for key in dict(data['calendar']).keys():
            work_days[int(key)-1] += [int(day) for day in range(1,days_in_month[int(key)-1]+1) if day not in data['calendar'][key]]
    except ValueError:
        print("calendar argument value error.")
        raise

    price_of_day = [salary / len(workday) for workday in work_days]

    # ---------------------- The computation -----------------------

    payments = dict()
    types = dict()

    for month in range(12):
        next_month = month + 1 if month != 11 else 0
        work_days_1 = pick_workdays(interval_1.start, interval_1.stop, work_days, days_in_month, month)
        work_days_2 = pick_workdays(interval_1.stop, interval_1.start, work_days, days_in_month, month)

        payday_1 = pick_payday(interval_1.start, day_advance+1, work_days, days_in_month, month)
        payday_2 = pick_payday(interval_1.stop, day_balance + 1, work_days, days_in_month, month)

        interval_1_payment = price_of_day[month] * len(work_days_1[0]) + price_of_day[next_month] * len(work_days_1[1])
        interval_2_payment = price_of_day[month] * len(work_days_2[0]) + price_of_day[next_month] * len(work_days_2[1])

        payment_date_1 = dt.date(year, (next_month if payday_1[1] else month)+1, payday_1[0])
        payment_date_2 = dt.date(year, (next_month if payday_2[1] else month)+1, payday_2[0])

        payments[payment_date_1] = interval_1_payment * (1-tax)
        payments[payment_date_2] = (interval_2_payment + bonus) * (1-tax)

        types[payment_date_1] = 'Advance'
        types[payment_date_2] = 'Balance'

    # ------------------------- The output -------------------------

    with open(output_fname, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter)
        writer.writerow([str(key).replace('-','.') for key in payments.keys()])
        writer.writerow([types[key] for key in payments.keys()])
        writer.writerow([str(int(round(val,0))) for val in payments.values()])

    print('Success.')



