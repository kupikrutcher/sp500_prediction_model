import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

df = pd.read_csv('https://docs.google.com/spreadsheets/d/1t2Bl9Jc0JCWOaeFgADJ2bVdoLdjDTWno/export?format=csv')

dateparse = lambda x: datetime.strptime(x, '%d.%m.%Y')

df['receiving_date'] = pd.to_datetime(df['receiving_date'], format = '%d.%m.%y', errors='coerce')

may_start_index = df[df['status'] == 'Май 2021'].index[0]  
june_start_index = df[df['status'] == 'Июнь 2021'].index[0]  
july_start_index = df[df['status'] == 'Июль 2021'].index[0]
aug_start_index = df[df['status'] == 'Август 2021'].index[0]
sep_start_index = df[df['status'] == 'Сентябрь 2021'].index[0]
oct_start_index = df[df['status'] == 'Октябрь 2021'].index[0]

df.loc[may_start_index:june_start_index, 'month'] = 'Май' 
df.loc[june_start_index:july_start_index, 'month'] = 'Июнь'
df.loc[july_start_index:aug_start_index, 'month'] = 'Июль'
df.loc[aug_start_index:sep_start_index, 'month'] = 'Август'
df.loc[sep_start_index:oct_start_index, 'month'] = 'Сентябрь'
df.loc[oct_start_index:, 'month'] = 'Октябрь'

df = df.rename(columns={'sum':'payment'})

df_1 = df
df_1 = df_1.rename(columns=({'new/current':'new_or_current'}))

df_1['payment'] = df_1['payment'].str.replace(',', '.')
df_1['payment'] = df_1['payment'].str.replace(' ', '')
df_1['payment'] = df_1['payment'].str.replace('\xa0', '')
df_1['payment'] = df_1['payment'].astype('float')
print(df_1)

# 1 task
revenue_2021 = df_1.query('status != "ПРОСРОЧЕНО" & month == "Июль"')\
    .agg({'payment':'sum'})
print(revenue_2021)

# 2 task
df_1_grouped = df_1.groupby('month').agg({'payment':'sum'})
sns.barplot(df_1_grouped, x='month', y='payment')
plt.show()

# 3 task
df_1.groupby(['sale', 'month'], as_index=False)\
    .agg({'payment':'sum'})\
        .query('month == "Сентябрь"')\
            .nlargest(1, 'payment')\
                .sale
# 4 task
df_1.query('month == "Октябрь"')\
    .groupby('new_or_current')\
        .agg({'new_or_current':'count'})\
            .nlargest(1, 'new_or_current')
# 5 task
df_1.query('month == "Июнь" & document == "оригинал"')\
    .groupby('document')\
        .agg({'new_or_current':'count'})

# Задание
df_1['receiving_date'] = pd.to_datetime(df_1['receiving_date'], format = '%d.%m.%y', errors='coerce')
df_1 = df_1.assign(month_receive = df_1['receiving_date'].dt.month_name())

df_2 = df_1.dropna(subset=['receiving_date'])\
    .query('receiving_date > "2021-07-01" & new_or_current == "новая" & status == "ОПЛАЧЕНО"')\
        .groupby(['sale', 'status', 'new_or_current'],as_index=False)\
            .agg({'payment':'sum'})\
                .assign(bonus=lambda x: x['payment'] / 100 * 7)

df_2_summed = df_2.groupby('sale', as_index=False).agg({'bonus':'sum'})

df_3 = df_1.dropna(subset=['receiving_date'])\
    .query('receiving_date > "2021-07-01" & new_or_current == "текущая" & status != "ПРОСРОЧЕНО" & payment > 10000')\
        .groupby(['sale', 'status', 'new_or_current'],as_index=False)\
            .agg({'payment':'sum'})\
                .assign(bonus=lambda x: x['payment'] / 100 * 5)

df_3_summed = df_3.groupby('sale', as_index=False).agg({'bonus':'sum'})

df_4 = df_1.dropna(subset=['receiving_date'])\
    .query('receiving_date > "2021-07-01" & new_or_current == "текущая" & status != "ПРОСРОЧЕНО" & payment < 10000')\
        .groupby(['sale', 'status', 'new_or_current'],as_index=False)\
            .agg({'payment':'sum'})\
                .assign(bonus=lambda x: x['payment'] / 100 * 3)

df_4_summed = df_4.groupby('sale', as_index=False).agg({'bonus':'sum'})

df_bonus = pd.merge(df_2_summed, df_3_summed, on='sale', how='outer') 
df_bonus = pd.merge(df_bonus, df_4_summed, on='sale', how='outer')  

df_bonus.fillna(0, inplace=True)
df_bonus['bonus_pretotal'] = df_bonus[['bonus_x', 'bonus_y', 'bonus']].sum(axis=1)

df_bonus_total = df_bonus['bonus_pretotal']


