import pandas as pd
import os
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import matplotlib.pyplot as plt

# === 1. Параметры ===
input_file = "7Regions_For_VIF.xlsx"  # путь к файлу
output_folder = "vif_tables_output"
os.makedirs(output_folder, exist_ok=True)

# === 2. Загрузка всех листов ===
xls = pd.ExcelFile(input_file)
sheet_names = xls.sheet_names

# === 3. Обработка каждого региона ===
for sheet in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)

    # Удалим целевую переменную, если она есть
    if "Real_Price_2023" in df.columns:
        df = df.drop(columns=["Real_Price_2023"])

    # Удалим пропущенные значения
    df_clean = df.dropna()

    if df_clean.shape[1] < 2:
        print(f"⚠️ Пропущен регион {sheet} — слишком мало переменных")
        continue

    # Добавим константу
    X = add_constant(df_clean)

    # Рассчитаем VIF
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

    # === 4. Визуализация VIF как таблицы ===
    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.5 * len(vif_data)))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=vif_data.round(3).values,
        colLabels=vif_data.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Сохранение
    safe_name = sheet.replace(" ", "_").replace("/", "_")[:30]
    plt.title(f"VIF Table - {sheet}", fontsize=14, pad=20)
    plt.savefig(f"{output_folder}/VIF_{safe_name}.png", bbox_inches='tight')
    plt.close()

print("✅ Все таблицы VIF сохранены как изображения.")