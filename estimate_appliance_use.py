from cv2 import CAP_PROP_XI_OUTPUT_DATA_PACKING_TYPE
import pandas as pd
import PySimpleGUI as sg


def import_house_csv():
    house_stats = pd.read_csv('data/house_stats.csv').drop('LocationId', 1)
    monthly_uses = pd.read_csv('data/monthly_uses.csv').drop('LocationID', 1)
    house_dict = dict(zip(house_stats.Property, house_stats.Value))
    # display_user_info(house_dict)
    useful_h_dict = {
        'total_use' : monthly_uses.TotalWh.iloc[-1],
        'cooking': {
            'last_month_use': monthly_uses.cooking.iloc[-1],
            'gas_stoves': house_dict['gas_stoves'],
            'gas_ovens': house_dict['gas_ovens'],
            'electric_stoves': house_dict['electric_stoves'],
            'electric_ovens': house_dict['electric_ovens'],
            'microwaves': house_dict['microwaves']},
        'fridge_freezer': {
            'last_month_use': monthly_uses.fridge_freezer.iloc[-1],
            'fridges': house_dict['fridges'],
            'freezers': house_dict['freezers'],
            'fridge_freezers': house_dict['fridge_freezers']}
    }
    return useful_h_dict


def calculate_usage(dict):
    cooking = dict['cooking']
    fridge_freezer = dict['fridge_freezer']

    total_cook = 0
    cook_aps = 0
    for ap, val in cooking.items():
        if ap == 'gas_stoves':
            cook_aps += int(val)
            total_cook += 1200 * int(val)
        if ap == 'gas_ovens':
            cook_aps += int(val)
            total_cook += 3000 * int(val)
        if ap == 'electric_stoves':
            cook_aps += int(val)
            total_cook += 1800 * int(val)
        if ap == 'electric_ovens':
            cook_aps += int(val)
            total_cook += 5000 * int(val)
        if ap == 'microwaves':
            cook_aps += int(val)
            total_cook += 1000 * int(val)

    total_ff = 0
    ff_aps = 0
    for ap, val in fridge_freezer.items():
        if ap == 'fridges':
            ff_aps += int(val)
            total_ff += 100 * int(val)
        if ap == 'freezers':
            ff_aps += int(val)
            total_ff += 150 * int(val)
        if ap == 'fridge_freezers':
            ff_aps += int(val)
            total_ff += 200 * int(val)

    avg_cook = total_cook / cook_aps
    avg_ff = total_ff / ff_aps
    cook_hours = cooking['last_month_use'] / avg_cook
    ff_hours = fridge_freezer['last_month_use'] / avg_ff
    return int(avg_cook), int(avg_ff), int(cook_hours), int(ff_hours)


def display_user_info(dict):

    table = [
        list(dict.values())
    ]
    print(table)

    headings = list(dict.keys())

    layout = [
        [sg.Table(values=table,
                  headings=headings,
                  max_col_width=35,
                  auto_size_columns=True,
                  display_row_numbers=False,
                  justification='right',
                  num_rows=10,
                  key='-TABLE-',
                  row_height=35)]
    ]

    window = sg.Window("Contact Information Window", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()


useful_h_dict = import_house_csv()
avg_cook, avg_ff, cook_hours, ff_hours = calculate_usage(useful_h_dict)
print(avg_cook)
print(avg_ff)
print(cook_hours)
print(ff_hours)
