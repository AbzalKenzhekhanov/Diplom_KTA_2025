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

# Создание папок
os.makedirs("correlation_heatmaps", exist_ok=True)
os.makedirs("correlation_heatmaps_with_emissions", exist_ok=True)

# Сильные корреляции
strong_corr_with_outliers = {}
strong_corr_without_outliers = {}

def remove_outliers_zscore(df, threshold=3):
    z_scores = np.abs((df - df.mean()) / df.std(ddof=0))
    return df[(z_scores < threshold).all(axis=1)]

def process_region(region, data, save_folder, target_dict, label):
    region_data = data[data["Country"] == region]
    numeric_data = region_data.select_dtypes(include="number").dropna()

    if numeric_data.shape[0] < 10 or "Real_Price_2023" not in numeric_data.columns:
        return

    if 'Year' in numeric_data.columns:
        numeric_data = numeric_data.drop(columns=["Year"])

    corr_matrix = numeric_data.corr()

    # Сохранение тепловой карты
    plt.figure(figsize=(24, 20))
    sns.heatmap(
        corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
        linewidths=0.5, annot_kws={"size": 10}, square=False
    )
    plt.title(f"{label} корреляционная матрица: {region}", fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()

    safe_region = region.replace(" ", "_").replace(".", "").replace("&", "and")
    plt.savefig(f"{save_folder}/heatmap_{safe_region}.png")
    plt.close()

    # Сохраняем сильные корреляции
    if "Real_Price_2023" in corr_matrix.columns:
        target_corr = corr_matrix["Real_Price_2023"].drop("Real_Price_2023", errors='ignore')
        strong_corr = target_corr[abs(target_corr) > 0.5].sort_values(ascending=False)
        target_dict[region] = strong_corr

# Обработка с выбросами
for region in regions_list:
    process_region(
        region=region,
        data=filtered_df,
        save_folder="correlation_heatmaps_with_emissions",
        target_dict=strong_corr_with_outliers,
        label="С выбросами"
    )

# Обработка без выбросов
filtered_no_outliers = filtered_df.copy()
numeric_cols = filtered_no_outliers.select_dtypes(include="number").columns
filtered_no_outliers[numeric_cols] = remove_outliers_zscore(filtered_no_outliers[numeric_cols])

for region in regions_list:
    process_region(
        region=region,
        data=filtered_no_outliers,
        save_folder="correlation_heatmaps",
        target_dict=strong_corr_without_outliers,
        label="Без выбросов"
    )

# Экспорт в Excel
with pd.ExcelWriter("Strong_Correlations_By_Region.xlsx") as writer:
    for region, corr_series in strong_corr_with_outliers.items():
        df = corr_series.reset_index()
        df.columns = ["Variable", "Correlation_with_Real_Price_2023"]
        df.to_excel(writer, sheet_name=f"{region[:28]}_with", index=False)

    for region, corr_series in strong_corr_without_outliers.items():
        df = corr_series.reset_index()
        df.columns = ["Variable", "Correlation_with_Real_Price_2023"]
        df.to_excel(writer, sheet_name=f"{region[:28]}_clean", index=False)

print("✅ Готово: тепловые карты и Excel-файл сохранены (с выбросами и без них).")