import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
regions_df = pd.read_excel("7Regions_Final_Cleaned.xlsx")
y_factor_df = pd.read_excel("Y_Factor.xlsx")

# Подготовка данных
filtered_df = regions_df[(regions_df["Year"] >= 1975) & (regions_df["Year"] <= 2023)].copy()
oil_price = y_factor_df.set_index("Year")["2023$cost"]
filtered_df["Real_Price_2023"] = filtered_df["Year"].map(oil_price)

# Список регионов
regions_list = filtered_df["Country"].unique()

# Создание папки
os.makedirs("correlation_heatmaps_with_emissions", exist_ok=True)
os.makedirs("vif_selected_correlations_with_emissions", exist_ok=True)

# Словарь для хранения выбранных переменных
selected_variables_by_region = {}

for region in regions_list:
    region_data = filtered_df[filtered_df["Country"] == region].copy()
    numeric_data = region_data.select_dtypes(include="number").dropna()

    if numeric_data.shape[0] < 10 or "Real_Price_2023" not in numeric_data.columns:
        continue

    if 'Year' in numeric_data.columns:
        numeric_data = numeric_data.drop(columns=["Year"])

    corr_matrix = numeric_data.corr()

    # Сохранение тепловой карты
    plt.figure(figsize=(24, 20))
    sns.heatmap(
        corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
        linewidths=0.5, annot_kws={"size": 10}, square=False
    )
    plt.title(f"Корреляционная матрица (с выбросами): {region}", fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()

    safe_region = region.replace(" ", "_").replace(".", "").replace("&", "and")
    plt.savefig(f"correlation_heatmaps_with_emissions/heatmap_{safe_region}.png")
    plt.close()

    # Выбор переменных с |r| > 0.5 с целевой переменной
    if "Real_Price_2023" in corr_matrix.columns:
        target_corr = corr_matrix["Real_Price_2023"].drop("Real_Price_2023", errors='ignore')
        strong_corr = target_corr[abs(target_corr) > 0.5].sort_values(ascending=False)
        selected_vars = []

        for var in strong_corr.index:
            if all(abs(corr_matrix[var][sel]) < 0.7 for sel in selected_vars):
                selected_vars.append(var)

        selected_df = pd.DataFrame({
            "Variable": selected_vars,
            "Correlation_with_Real_Price_2023": [target_corr[v] for v in selected_vars]
        })
        selected_variables_by_region[region] = selected_df

# Экспорт в Excel
with pd.ExcelWriter("vif_selected_correlations_with_emissions/AfricaVIFtablesDatas_with_emissions.xlsx") as writer:
    for region, df in selected_variables_by_region.items():
        sheet_name = region[:31]  # Excel ограничение
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("✅ Готово: корреляции с выбросами сохранены и отобраны переменные.")