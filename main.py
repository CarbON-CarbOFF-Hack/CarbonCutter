import PySimpleGUI as sg

sg.theme('BluePurple')

layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Show'), sg.Button('Exit')]]

window = sg.Window('Pattern 2B', layout)

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    print(type(event))
    print(type(values))
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
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
    import_csvs('data/')
    run_model(dataframe)

    # USER IS SHOWN GRAPH OF PAST ENERGY USE AND PREDICTED FUTURE ENERGY USE,
    # AS WELL AS THE ESTIMATED WAYS THEY USED ENERGY IN THE LAST MONTH

    display_info(model_output, df)

    # USER IS THEN PROMPTED 
