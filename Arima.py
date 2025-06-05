import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import numpy as np
import os

# === 1. Настройка ===
file_path = "7Regions_For_Arima.xlsx"  # путь к файлу
output_folder = "ArimaResults"
os.makedirs(output_folder, exist_ok=True)

# === 2. Загрузка всех листов ===
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names
results_summary = {}

# === 3. Обработка каждого региона ===
for sheet in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    if "Year" not in df.columns or "Real_Price_2023" not in df.columns:
        continue

    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.set_index("Year", inplace=True)

    y = df["Real_Price_2023"].dropna()
    X = df.drop(columns=["Real_Price_2023", "Year"], errors="ignore")
    X = X.loc[y.index]

    # === 4. ADF-тест ===
    result = adfuller(y)
    pvalue = result[1]
    d = 0 if pvalue < 0.05 else 1

    # === 5. ADF-график ===
    fig, ax = plt.subplots()
    ax.plot(y)
    ax.set_title(f"{sheet} – Real_Price_2023 (p-value ADF = {pvalue:.4f})")
    plt.savefig(os.path.join(output_folder, f"{sheet}_ADF.png"), dpi=300)
    plt.close()

    # === 6. ACF и PACF ===
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(y.diff().dropna() if d == 1 else y, ax=axes[0], lags=10)
    plot_pacf(y.diff().dropna() if d == 1 else y, ax=axes[1], lags=10)
    axes[0].set_title("ACF")
    axes[1].set_title("PACF")
    plt.suptitle(f"{sheet} – ACF / PACF")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{sheet}_ACF_PACF.png"), dpi=300)
    plt.close()

    # === 7. Автоподбор ARIMAX ===
    best_aic = np.inf
    best_order = None
    best_model = None
    warnings.filterwarnings("ignore")

    for p in range(3):
        for q in range(3):
            try:
                model = SARIMAX(y, exog=X, order=(p, d, q), seasonal_order=(0, 0, 0, 0))
                model_fit = model.fit(disp=False)
                if model_fit.aic < best_aic:
                    best_aic = model_fit.aic
                    best_bic = model_fit.bic
                    best_order = (p, d, q)
                    best_model = model_fit
            except:
                continue

    if best_model is None:
        continue

    # === 8. Диагностика остатков ===
    best_model.plot_diagnostics(figsize=(12, 8))
    plt.suptitle(f"{sheet} – Диагностика ARIMAX{best_order}")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{sheet}_Diagnostics.png"), dpi=300)
    plt.close()

    # === 9. Прогноз ===
    forecast_steps = 5
    future_index = pd.date_range(start=y.index[-1] + pd.DateOffset(years=1), periods=forecast_steps, freq='Y')
    last_X = X.iloc[-1:]
    future_X = pd.concat([last_X] * forecast_steps)
    future_X.index = future_index

    forecast = best_model.get_forecast(steps=forecast_steps, exog=future_X)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()
    x_vals = pd.to_datetime(forecast_mean.index)
    conf_int_lower = conf_int.iloc[:, 0].astype(float).values
    conf_int_upper = conf_int.iloc[:, 1].astype(float).values

    # === 10. График прогноза ===
    plt.figure(figsize=(10, 6))
    plt.plot(y, label="Фактические данные", color="blue")
    plt.plot(x_vals, forecast_mean.values, label="Прогноз ARIMAX", linestyle="--", color="red")
    plt.fill_between(x_vals, conf_int_lower, conf_int_upper,
                     color='gray', alpha=0.3, label="95% доверительный интервал")
    plt.title(f"{sheet} – Прогноз ARIMAX{best_order}")
    plt.xlabel("Год")
    plt.ylabel("Real_Price_2023")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{sheet}_Forecast.png"), dpi=300)
    plt.close()

    # === 11. Сохраняем AIC + BIC ===
    results_summary[sheet] = {
        "ARIMAX_order": best_order,
        "ADF_pvalue": round(pvalue, 4),
        "AIC": round(best_aic, 2),
        "BIC": round(best_bic, 2)
    }

# === 12. Таблица итогов ===
summary_df = pd.DataFrame.from_dict(results_summary, orient='index')
summary_df.index.name = "Регион"
summary_df.to_excel(os.path.join(output_folder, "ARIMAX_Summary.xlsx"))

print("✅ Готово: модели построены, прогнозы и метрики AIC/BIC сохранены в папке ArimaResults/")