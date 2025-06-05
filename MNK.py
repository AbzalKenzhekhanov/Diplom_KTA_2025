import statsmodels.api as sm
import pandas as pd

# Файл жолдары
input_path = "7Regions_For_VIF.xlsx"
output_txt_path = "OLS_Results_Summary.txt"

# Excel парақтары
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# Нәтижені жинау
with open(output_txt_path, "w", encoding="utf-8") as f:
    for sheet in sheet_names:
        df = pd.read_excel(input_path, sheet_name=sheet)
        if "Real_Price_2023" not in df.columns:
            continue
        y = df["Real_Price_2023"]
        X = df.drop(columns=["Real_Price_2023"])
        X = sm.add_constant(X)

        try:
            model = sm.OLS(y, X).fit()
            f.write(f"\n\n===== Аймақ: {sheet} =====\n")
            f.write(model.summary().as_text())
        except Exception as e:
            f.write(f"\n\n===== Аймақ: {sheet} =====\n")
            f.write(f"Қате: {str(e)}")