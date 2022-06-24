# from ossaudiodev import SNDCTL_DSP_GETBLKSIZE
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import sklearn.metrics as metrics
from sklearn.metrics import make_scorer
from scipy.signal import savgol_filter
import plotly.graph_objects as go


def calc_hourmin(hour, minute):
    return hour + minute / 60


def calc_hour_x(hourmin):
    return np.sin((360 / 24) * hourmin)


def calc_hour_y(hourmin):
    return np.cos((360 / 24) * hourmin)


def calc_day_x(end_of_month, day):
    return np.sin((360 / end_of_month) * day)


def calc_day_y(end_of_month, day):
    return np.cos((360 / end_of_month) * day)


def calc_month_x(month):
    return np.sin((360 / 12) * month)


def calc_month_y(month):
    return np.cos((360 / 12) * month)


def regression_results(y_true, y_pred):
    # Regression metrics
    explained_variance = metrics.explained_variance_score(y_true, y_pred)
    mean_absolute_error = metrics.mean_absolute_error(y_true, y_pred)
    mse = metrics.mean_squared_error(y_true, y_pred)
    mean_squared_log_error = metrics.mean_squared_log_error(y_true, y_pred)
    median_absolute_error = metrics.median_absolute_error(y_true, y_pred)
    r2 = metrics.r2_score(y_true, y_pred)
    # print('explained_variance: ', round(explained_variance,4))
    # print('mean_squared_log_error: ', round(mean_squared_log_error,4))
    # print('r2: ', round(r2,4))
    # print('MAE: ', round(mean_absolute_error,4))
    # print('MSE: ', round(mse,4))
    print('RMSE: ', round(np.sqrt(mse), 4))
    return np.sqrt(mse)


def rmse(actual, predict):
    predict = np.array(predict)
    actual = np.array(actual)
    distance = predict - actual
    square_distance = distance ** 2
    mean_square_distance = square_distance.mean()
    score = np.sqrt(mean_square_distance)
    return score


def train(data, shift_str, rmse_score):
    X_train = data[:'2021'].drop(['Energy (wh)'], axis=1)
    y_train = data.loc[:'2021', 'Energy (wh)']
    X_test = data['2022'].drop(['Energy (wh)'], axis=1)
    y_test = data.loc['2022', 'Energy (wh)']
    # normalise day of week column using min-max scaling
    scaler = MinMaxScaler()
    cols_to_norm = [shift_str, 'Day of the week']
    X_train[cols_to_norm] = scaler.fit_transform(X_train[cols_to_norm])
    X_test[cols_to_norm] = scaler.transform(X_test[cols_to_norm])
    model = RandomForestRegressor()
    param_search = {
        # 'n_estimators': [20, 50, 100],
        # 'max_features': ['auto', 'sqrt', 'log2'],
        # 'max_depth' : [i for i in range(5,15)]
        'n_estimators': [50],
        'max_features': ['auto'],
        'max_depth': [i for i in range(5, 10)]
    }
    tscv = TimeSeriesSplit(n_splits=10)
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring=rmse_score)
    gsearch.fit(X_train, y_train)
    best_score = gsearch.best_score_
    best_model = gsearch.best_estimator_
    y_true = y_test.values
    y_pred = best_model.predict(X_test)
    RMSE = regression_results(y_true, y_pred)
    return y_pred, RMSE


def get_models(df_days):
    # Extract dates from dataframe
    dates = df_days.index
    # Extract year, month, day, hour and minutes from datetime entities to calculate
    # 2d time
    years = dates.year
    months = dates.month
    days = dates.day
    # hours = dates.hour
    minutes = dates.minute
    # create list of end_of_month (number of days in that month) for each month
    longest_months = [1, 3, 5, 7, 8, 10, 12]
    end_of_month = []
    for m in months:
        if m in longest_months:
            end_of_month.append(31)
        elif m == 2:
            end_of_month.append(28)
        else:
            end_of_month.append(30)

    end_of_month = np.array(end_of_month)
    day_x = calc_day_x(end_of_month, days)
    day_y = calc_day_y(end_of_month, days)
    month_x = calc_month_x(months)
    month_y = calc_month_y(months)
    day_of_week = dates.dayofweek

    time_features = np.vstack([day_x, day_y, month_x, month_y, day_of_week])
    headers = ['Day_x', 'Day_y', 'Month_x', 'Month_y', 'Day of the week']
    df_2d_time = df_days.copy()
    for i, h in enumerate(headers):
        df_2d_time[h] = time_features[i]
    is_weekday = [0 if day_idx in [5, 6] else 1 for day_idx in dates.weekday]
    is_season_winter = [1 if month in [11, 12, 1, 2] else 0 for month in dates.month]
    dummy_vars = np.vstack([is_weekday, is_season_winter])

    headers = ['is_weekday', 'is_season_winter']
    df_dummy = df_2d_time.copy()
    for i, h in enumerate(headers):
        df_dummy[h] = dummy_vars[i]

    rmse_score = make_scorer(rmse, greater_is_better=False)

    y_preds = []
    stds = []

    for day_shift in range(1, 8):
        # ADD WEEK SHIFT
        df_shifts = df_dummy.copy()
        shift_str = str(day_shift) + 'day shift'
        df_shifts[shift_str] = df_shifts['Energy (wh)'].shift(day_shift)
        df_shifts = df_shifts.dropna()
        y_pred, RMSE = train(df_shifts, shift_str, rmse_score)
        y_preds.append(y_pred)
        stds.append(RMSE)

    return y_preds, stds


def plot_forecast(df_shifts, y_preds, stds):
    X = df_shifts.index
    y = df_shifts['Energy (wh)']
    prev = 14
    split_id = len(df_shifts[:'2021'].index)
    X_prev = X[split_id - prev:split_id]
    y_prev = y[split_id - prev:split_id]
    X_fut = X[split_id - 1:split_id + 7]
    y_fut = []
    for i in range(7):
        y_pred = y_preds[i]
        y_fut.append(y_pred[i])
    y_fut.insert(0, y_prev[-1])
    errors = stds.copy()
    errors = np.insert(errors, 0, 0)
    y_fut = np.array(y_fut)
    # print(y_fut.shape, stds.shape)

    # fig = plt.figure(figsize=[12, 6])
    # plt.plot(X_prev, y_prev, color='blue')
    # plt.plot(X_fut, y_fut, color='green')
    # plt.fill_between(X_fut, y_fut - errors, y_fut + errors, alpha=0.3, color='green')
    # plt.legend()
    # plt.show()

    return X_prev, y_prev, X_fut, y_fut, errors


def plot_past(X_prev, y_prev):
    colors = ['aqua', 'violet', 'limegreen']
    fig = go.Figure(go.Scatter(
        name='existing data',
        x=X_prev,
        y=y_prev,
        line=dict(color='blue'),
        mode='lines'
    )
    )

    fig.show()


def plot_reductions(X_prev, y_prev, X_fut, y_fut, errors, reductions=[0]):
    colors = ['aqua', 'violet', 'limegreen']
    fig = go.Figure(go.Scatter(
        name='existing data',
        x=X_prev,
        y=y_prev,
        line=dict(color='blue'),
        mode='lines'
    )
    )

    for i, reduction in enumerate(reductions):
        new = y_fut.copy()
        # new_errors = errors.copy()
        new[1:] = new[1:] - reduction
        # new_errors[1:] = new_errors[1:] - reduction
        y_upper = new + errors
        y_lower = new - errors
        if reduction == 0:
            name = 'predicted future consumption'
        else:
            name = 'reducing your consumption by ' + str(reduction) + ' CO2e'
        if i == 0:
            visible = True
        else:
            visible = 'legendonly'
        fig.add_trace(
            go.Scatter(
                name=name,
                x=X_fut,
                y=new,
                line=dict(color=colors[i]),
                mode='lines',
                visible=visible
            )
        )
        fig.add_trace(
            go.Scatter(
                name=name + ' upper',
                x=X_fut,  # x, then x reversed
                y=y_upper,  # upper, then lower reversed
                mode='lines',
                marker=dict(color=colors[i]),
                line=dict(width=0),
                visible=visible,
                opacity=0.2
                # showlegend=False
            )
        )
        fig.add_trace(
            go.Scatter(
                name=name + ' lower',
                x=X_fut,  # x, then x reversed
                y=y_lower,  # upper, then lower reversed
                marker=dict(color=colors[i]),
                line=dict(width=0),
                mode='lines',
                # fillcolor=colors[i],
                fill='tonexty',
                opacity=0.2,
                visible=visible
            )
        )
    fig.show()
