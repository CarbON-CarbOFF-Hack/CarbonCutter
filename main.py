import PySimpleGUI as sg
import requests
import json
from requests.structures import CaseInsensitiveDict
import pandas as pd
import matplotlib.pyplot as plt
from estimate_appliance_use import import_house_csv, calculate_usage
from model import get_models, plot_forecast, plot_reductions


# sg.theme('BluePurple')
#
# layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15,1), key='-OUTPUT-')],
#           [sg.Input(key='-IN-')],
#           [sg.Button('Show'), sg.Button('Exit')]]
#
# window = sg.Window('Pattern 2B', layout)
#
# while True:  # Event Loop
#     event, values = window.read()
#     print(event, values)
#     print(type(event))
#     print(type(values))
#     if event == sg.WIN_CLOSED or event == 'Exit':
#         break
#     if event == 'Show':
#         # Update the "output" text element to be the value of "input" element
#         window['-OUTPUT-'].update(values['-IN-'])
#
# window.close()


def import_data(URL):
    """
    take in filepath or api call, and create dataframes relevant for different models
    return model_df, model
    """
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2NTUzODA0NTYsImV4cCI6MTY1NjAyMTYwMCwiaWF0IjoxNjU1Mzgw' \
            'NDU2LCJpc3MiOiJlbGlxIiwiYXVkIjoiZWxpcV9hcGlfdjMiLCJjbGllbnRJZCI6Nzk4MjM1NTg3OCwidXNlcklkIjoyMzgyMjUzL' \
            'CJyb2xlcyI6W10sImlzUmVhZE9ubHkiOnRydWV9.DMTF-ST2tpaN_MUq_mIfVr90oYxRl5_OiJMKszQ8mIQ'
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = 'Bearer ' + token

    response_API = requests.get(URL, headers=headers)
    print(response_API)
    data = response_API.text
    return data


def draw_plot():
    plt.plot([0.1, 0.2, 0.5, 0.7])
    plt.show(block=False)


def gui_loop():
    useful_h_dict = import_house_csv()
    avg_cook, avg_ff, cook_hours, ff_hours = calculate_usage(useful_h_dict)
    total_use = useful_h_dict['total_use']

    sg.theme('BluePurple')

    layout = [
        [
            sg.Text(f'Your last month\'s energy use was: {total_use}wh', font=('Any 15')),
        ],
        [
            sg.Text(f'Which is {int(0.000223 * total_use)}kg of CO2e', font=('Any 15')),
        ],
        [
            sg.Button('Plot last month', font=('Any 15'))
        ],
        [
            sg.Text('From your energy use for cooking we calculate you cooked for:', font=('Any 15'))
        ],
        [
            sg.Text(f'{cook_hours} hours', font=('Any 15'))
        ],
        [
            sg.Text(
                'From your energy use for fridge/freezer we calculate you had your fridge-freezer appliances on for:',
                font=('Any 15'))
        ],
        [
            sg.Text(f'{ff_hours} hours', font=('Any 15'))
        ],
        [
            sg.Text(f'Your predicted next week\'s energy use is: {int(total_use / 4)}wh', font=('Any 15')),
        ],
        [
            sg.Text(f'Which is {int(0.000223 * total_use / 4)}kg of CO2e', font=('Any 15')),
        ],
        [
            sg.Button('Plot next week', font=('Any 15'))
        ],
        [
            sg.Text('If you cooked for 2 hours less next week, you could reduce your next week CO2e to:',
                    font=('Any 15'))
        ],
        [
            sg.Text(f'{int(0.000223 * (total_use / 4 - avg_cook * 4))}kg', font=('Any 15'))
        ],
        [
            sg.Button('Plot compared forecasted energy', font=('Any 15'))
        ],
        [
            sg.Button('Exit', font=('Any 15'))
        ]
    ]

    window = sg.Window('Carbon Cutter', layout)

    while True:  # Event Loop
        event, values = window.read()
        avg_cook, avg_ff, cook_hours, ff_hours = calculate_usage(useful_h_dict)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Plot last month':
            draw_plot()
        if event == 'Plot next week':
            draw_plot()
        if event == 'Plot compared forecasted energy':
            draw_plot()
        if event == 'Show':
            # Update the "output" text element to be the value of "input" element
            window['-OUTPUT-'].update(values['-IN-'])

    window.close()


def convert_json_to_dataframe(data):
    """
    convert data in json format to a pandas dataframe
    """
    # extract start and end dates of dataset
    data_dict = json.loads(data)
    start_date = data_dict['from']
    end_date = data_dict['to']

    # convert to pandas dataframe
    df = pd.read_json(data)
    # drop columns that aren't relevant to prediction
    df = df.drop(['resolution', 'from', 'to', 'fuel', 'unit'], axis=1)
    # rename 'consumption' column to included unit
    df = df.rename(columns={'consumption': 'Energy (wh)'})
    df['Energy (wh)'] = df['Energy (wh)'].astype(float, errors='raise')
    # index energy consumption values by day
    df['Local datetime'] = pd.date_range(start=start_date, periods=len(df), freq='D')
    df = df.set_index('Local datetime')
    return df


def run_model(dataframe):
    """
    run model on data to predict future outcomes
    return model_output
    """
    y_preds, stds = get_models(dataframe)
    X_prev, y_prev, X_fut, y_fut, errors = plot_forecast(dataframe, y_preds, stds)
    plot_reductions(X_prev, y_prev, X_fut, y_fut, errors)


def display_info(model_output, df):
    """
    display model graph through simple gui
    """
    pass


if __name__ == '__main__':
    # ON RUNNING APPLICATION, DATA ABOUT HOUSEHOLD IS IMPORTED FROM 3 CSVs AND USED TO RUN MODEL LIVE
    # load consumption data using location id: 2448401
    location_id = '2448401'
    queryURL = 'https://api-v3.eliq.io/v3/locations/' + location_id + '/consumption?resolution=day&from=2021-01-01&to=2022-06-01'
    data_json = import_data(queryURL)
    dataframe = convert_json_to_dataframe(data_json)

    run_model(dataframe)
    # df = import_csvs('data/')
    model_output = run_model(dataframe)

    # USER IS SHOWN GRAPH OF PAST ENERGY USE AND PREDICTED FUTURE ENERGY USE,
    # AS WELL AS THE ESTIMATED WAYS THEY USED ENERGY IN THE LAST MONTH

    # display_info(model_output, df)

    # USER IS THEN PROMPTED
    # USER IS THEN PROMPTED

    gui_loop()
