import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from math import sqrt
import warnings
warnings.filterwarnings('ignore')


def predict_price(num_of_weeks):
    df = pd.read_csv("df_merged_cleaned_highest_corr.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    Xgb = df.drop(columns=['Цена на арматуру', 'Date', 'Лом_3А, РФ CPT ж/д Южный ФО, руб./т, без НДС', 'Лом_3А, РФ CPT ж/д Центральный ФО, руб./т, без НДС', 'Лом_3А, РФ FCA ж/д респ. Татарстан, руб./т, без НДС', 'Лом_3А, РФ FCA ж/д Московский регион, руб./т, без НДС', 'Лом_3А, РФ CPT ж/д Уральский ФО, руб./т, без НДС', 'Чугун_CFR Турция, $/т'])
    ygb = df['Цена на арматуру']
    Xgb['rolling_mean'] = ygb.rolling(window=3, min_periods=1).mean()

    for _ in range(num_of_weeks):

        # Определяем модель
        xgb_model = XGBRegressor()

        # Подгоняем модель на данных
        xgb_model.fit(Xgb[:-1], ygb[:-1])

        # Прогнозируем на тестовых данных
        ygb_pred = xgb_model.predict(Xgb[-1:])

        # Оцениваем модель
        # mae = mean_absolute_error(ygb[-1:], ygb_pred)
        # r2 = r2_score(ygb[-1:], ygb_pred)
        # rmse = sqrt(mean_squared_error(ygb[-1:], ygb_pred))

        # print(f"MAE score: {mae}")
        # print(f"R2 score: {r2}")
        # print(f"RMSE score: {rmse}")
        ygb = pd.concat([ygb, pd.Series(round(int(ygb_pred), -2))], ignore_index=True)
        missing_rows = len(ygb) - len(Xgb)
        empty_data = pd.DataFrame(index=range(missing_rows), columns=Xgb.columns)
        Xgb = pd.concat([Xgb, empty_data], ignore_index=True)
        Xgb['rolling_mean'] = ygb.rolling(window=3, min_periods=1).mean()

    return(ygb[-num_of_weeks:])

# predict_price()