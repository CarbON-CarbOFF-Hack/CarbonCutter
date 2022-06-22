import pandas as pd
import PySimpleGUI as sg


def import_csvs():
    house_stats = pd.read_csv('data/house_stats.csv').drop('LocationId', 1)
    house_dict = dict(zip(house_stats.Property, house_stats.Value))
    display_user_info(house_dict)
    useful_h_dict = {
        'cooking': [],
        'fridge_freezer': []
    }


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


import_csvs()
