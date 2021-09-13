WARNING: A LITTLE BIT OUTDATED

WARNING: A LITTLE BIT OUTDATED

WARNING: A LITTLE BIT OUTDATED

Income prediction
-----------------

To calculate income days and income value per these days.

### 1. Usage: ###

> income.py [--input <file_name>] [--output <file_name>]

If the <file_name> for input or output is not specified, the script uses default filenames "input.json" and "output.csv" respectively.

For input file format see sec. 3

### 2. Details ###

Income includes base salary (salary) and bonus payment (bonus) and is split into two parts: advance and balance, by the following rules:

* Advance payment
  * workdays is counted from 1'st to 15'th (inclusive) of the month
  * Paid at nearest to 20'th workday for the last 1-15'th
  * = amount_of_workdays ✕ workday_cost
* Balance payment
  * workdays is counted from 16'st to 31'th (inclusive) of the month
  * Paid at nearest to 5'th workday for the last 16-31'th
  * = amount_of_workdays ✕ workday_cost ＋ premium_payment
  

The salary and bonus values are assumed as fixed (const).

### 3. Input: ###
Workdays of each month.

#### Format ####
JSON format is used. There is several parameters:

* Basically, the year, salary (per month) and bonus (per month)
  
  > year=[int]
* workdays calendar in format {month: list of days, month: list of days, ...}
  
  > calendar: {**month** as *int* : **workdays** as *[int, int, int, ...]*, ..., ... }
* additional (non-regular) income like {date:amount, date:amount, ...}
  
  > additional: {**date** as *date*: **amount** as *int*,  ..., ...} 
  
  Using month[days] representation for workdays calendar whereas date representation for additional income is assumed to be more ergonomic/practical.
  For instance, one can use additional as the vacation payments.

#### Example ####
> {
> year: 2022,
> salary: 10000,
> bonus: 5000,
> calendar : {
> 1: [1,2,3,4,5,6,7,8,9,15,16,22,23,29,30],
> 2: [5,6,12,13,19,20,22,23,26,27],
> 3: [5,6,7,8,12,13,19,20,26,27],
> 4: [2,3,9,10,16,17,23,24,30],
> 5: [1,2,7,8,9,14,15,21,22,28,29],
> 6: [4,5,11,12,13,18,19,25,26],
> 7: [2,3,9,10,16,17,23,24,30,31],
> 8: [6,7,13,14,20,21,27,28],
> 9: [3,4,10,11,17,18,24,25],
> 10: [1,2,8,9,15,16,22,23,29,30],
> 11: [3,4,5,6,12,13,19,20,26,27],
> 12: [3,4,10,11,17,18,24,25,31]
> }


### 4. Output ###
#### Format ####

### 5. Logic ###
1. Read input.json.
2. For each month call income(year as int, month as int, days-off as list[int])
Retrieve days off from input or in other ways (if implemented)
3. Count number of workdays based on subtracting days off
4. 
