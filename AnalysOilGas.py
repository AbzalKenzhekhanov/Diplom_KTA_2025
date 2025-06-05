import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Загрузка данных из Excel
file_path = 'Datas.xlsx'  # Указываем путь к файлу
data = pd.read_excel(file_path)

# Загрузка цен на нефть (Y-фактор)
y_data_raw = pd.read_excel('Y_Factor.xlsx')

# Очистка и переименование колонок
y_data = y_data_raw.iloc[3:].copy()
y_data.columns = ["Year", "Nominal_Price", "Real_Price_2023"]
y_data.dropna(inplace=True)
y_data["Year"] = y_data["Year"].astype(int)
y_data["Real_Price_2023"] = y_data["Real_Price_2023"].astype(float)

# Фильтрация по годам, которые есть в исходных данных
y_data = y_data[y_data["Year"].between(data["Year"].min(), data["Year"].max())]

# Объединение данных по году
merged_data = pd.merge(data, y_data[["Year", "Real_Price_2023"]], on="Year", how="left")

# Проверка результата
print(merged_data[["Year", "Real_Price_2023"]].dropna().head())

# Сохранение объединенных данных
merged_data.to_excel('Merged_Data.xlsx', index=False)

# Проверка первых нескольких строк данных
print(data.head())

# Проверка типов данных
print(data.dtypes)

# Проверка на пропущенные значения
print(data.isna().sum())

# Получение статистики по числовым данным
print(data.describe())

# Сохранение обработанных данных в новый Excel файл
data.to_excel('Processed_Data.xlsx', index=False)

# Аймақтар тізімі
regions = [
    "Total North America",
    "Total S. & Cent. America",
    "Total Europe",
    "Total CIS",
    "Total Middle East",
    "Total Africa",
    "Total Asia Pacific"
]

# Аймақтық деректерді сақтайтын сөздік
regional_data = {}

# Әр өңір бойынша сүзу
for region in regions:
    regional_data[region] = merged_data[merged_data["Country"] == region].copy()

# Мысал ретінде бір аймақты қарап шығайық
print(regional_data["Total Europe"].head())

# 5. Аймақтар бойынша сипаттамалық статистика
variables_to_describe = ["primary_ej", "oilprod_kbd", "Real_Price_2023"]
regional_stats = []

for region in regions:
    region_df = merged_data[merged_data["Country"] == region]
    stats = region_df[variables_to_describe].describe().loc[["mean", "std", "min", "max"]]
    stats["Region"] = region
    regional_stats.append(stats)

summary_df = pd.concat(regional_stats)
summary_df.reset_index(inplace=True)
summary_df.rename(columns={"index": "Statistic"}, inplace=True)
summary_df = summary_df[["Region", "Statistic"] + variables_to_describe]

# 6. Нәтижені көрсету немесе сақтау
print(summary_df)
summary_df.to_excel("Regional_Statistics.xlsx", index=False)  # қажет болса сақтау

# 1. Жүкте негізгі деректер (уже у тебя есть)
data = pd.read_excel("Processed_Data.xlsx")  # Или путь к твоему файлу с полными данными

# 2. Жүкте жаңартылған деректер (взяты из "Central_America_Complete_25plus.xlsx")
updated_df = pd.read_excel("Central_America_Complete_25plus.xlsx")

# 3. Удалим все строки по "Total S. & Cent. America"
data = data[data["Country"] != "Total S. & Cent. America"]

# 4. Добавим обновленные строки
data = pd.concat([data, updated_df], ignore_index=True)

# 5. (Необязательно) Сақтап қоюға болады
data.to_excel("Processed_Data_Updated.xlsx", index=False)

print("Central America обновлены. Всего строк по этому региону:", 
      data[data["Country"] == "Total S. & Cent. America"].shape[0])