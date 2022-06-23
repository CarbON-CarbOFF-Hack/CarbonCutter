import PySimpleGUI as sg
import matplotlib.pyplot as plt

from estimate_appliance_use import import_house_csv, calculate_usage


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
            sg.Text(f'Which is {int(0.000223*total_use)}kg of CO2e', font=('Any 15')),
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
            sg.Text('From your energy use for fridge/freezer we calculate you had your fridge-freezer appliances on for:', font=('Any 15'))
        ],
        [
            sg.Text(f'{ff_hours} hours', font=('Any 15'))
        ],
        [
            sg.Text(f'Your predicted next week\'s energy use is: {int(total_use/4)}wh', font=('Any 15')),
        ],
        [
            sg.Text(f'Which is {int(0.000223*total_use/4)}kg of CO2e', font=('Any 15')),
        ],
        [
            sg.Button('Plot next week', font=('Any 15'))
        ],
        [
            sg.Text('If you cooked for 2 hours less next week, you could reduce your next week CO2e to:', font=('Any 15'))
        ],
        [
            sg.Text(f'{int(0.000223*(total_use/4 - avg_cook * 4))}kg', font=('Any 15'))
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


def import_csvs(filepath):
    """
    take in filepath or api call, and create dataframes relevant for different models
    return model_df, model
    """
    pass


def run_model(dataframe):
    """
    run model on data to predict future outcomes
    return model_output
    """
    pass


def display_info(model_output, df):
    """
    display model graph through simple gui
    """
    pass


if __name__ == '__main__':
    # ON RUNNING APPLICATION, DATA ABOUT HOUSEHOLD IS IMPORTED FROM 3 CSVs AND USED TO RUN MODEL LIVE
    df = import_csvs('data/')
    model_output = run_model(df)

    # USER IS SHOWN GRAPH OF PAST ENERGY USE AND PREDICTED FUTURE ENERGY USE,
    # AS WELL AS THE ESTIMATED WAYS THEY USED ENERGY IN THE LAST MONTH

    # USER IS THEN PROMPTED

    gui_loop()
