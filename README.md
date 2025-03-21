# Assignment Katekima

## Task

### Assignment 1
Linear Feedback Shift Register (LFSR) Implementation

HOW TO RUN
```sh
cd assigment_1

python lfsr.py
```

### Assignment 2 (Django Project)
Stock Warehouse

### Requirements
- python >= 3.9
- django >= 4.2.20
- djangorestframework >= 3.15.2

### HOW TO RUN
1. active virtual environtment

```sh
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```
NOTE:
```
The command to activate the environment applies to Mac and Linux OS. 
If you are running it on Windows, please check the docs yourself to activate it.
```

2. Then, Open assigment_2,
```sh
cd assigment_2
```
3. Load Dummy data
```sh
python manage.py loaddata fixtures/initial_data.json
```
4. Run server django
```sh
python manage.py runserver
```
### LIST ENDPOINT FULL
Please read file `description.pdf`

### EXAMPLE for Report
Try get endpoint
```
[ GET ] /api/report/ITEM005/?start_date=2024-01-01&end_date=2025-03-31
```