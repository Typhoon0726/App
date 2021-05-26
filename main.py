import pyodbc
import pandas as pd
from fastapi import FastAPI
from typing import Optional
import uvicorn

app = FastAPI()

cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=tcp:2021-report.database.windows.net,1433;Database=System;Uid={C107156216@o365.nkust.edu.tw};Pwd={Typhoon890726};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword')
cursor = cnxn.cursor()


@app.get('/')
async def get_data():
    query_veg = "SELECT TOP 1 作物名稱 AS Name,平均價 AS Price FROM dbo.Veg ORDER BY 平均價 ASC"
    df_veg = pd.read_sql(query_veg, cnxn)
    df_m = df_veg.to_dict('r')
    query_fish = "SELECT TOP 1 魚貨名稱 AS Name,魚貨價格 AS Price FROM dbo.Fish ORDER BY 魚貨價格 ASC"
    df_fish = pd.read_sql(query_fish, cnxn)
    df_m += df_fish.to_dict('r')
    return df_m


@app.get('/price/veg/{veg}')
async def get_Price_Veg(veg: str):
    if veg == '便宜':
        query = "SELECT TOP 1 作物名稱 AS Name,平均價 AS Price FROM dbo.Veg ORDER BY 平均價 ASC"
    else:
        if veg:
            veg_n = veg.split(',')
        Price_1 = {'veg': veg_n}
        query = "SELECT 作物名稱 AS Name,平均價 AS Price FROM dbo.Veg WHERE "
        for i in range(0, len(Price_1['veg'])):
            query += "作物名稱 LIKE (N'%"+Price_1['veg'][i]+"%') "
            if i != len(Price_1['veg'])-1:
                query += "OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/price/meat/{meat}')
async def get_Price_Meat(meat: str):
    if meat:
        meat_n = meat.split(',')
    Price_2 = {'meat': meat_n}
    query = "SELECT TOP 1 "
    for i in range(0, len(Price_2['meat'])):
        if Price_2['meat'][i] == '雞肉':
            query += '"白肉雞(門市價高屏)" AS NameA '
            if len(Price_2['meat']) >= 2 and i == 0:
                query += ","
        elif Price_2['meat'][i] == '雞蛋':
            query += '"雞蛋(產地)" AS NameB'
            if len(Price_2['meat']) >= 2 and i == 0:
                query += ","
    query += " FROM dbo.Meat"
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/price/fish/{fish}')
async def get_Price_Fish(fish: str):
    if fish == '便宜':
        query = "SELECT TOP 1 魚貨名稱 AS Name,魚貨價格 AS Price FROM dbo.Fish ORDER BY 魚貨價格 ASC"
    else:
        if fish:
            fish_n = fish.split(',')
        Price_3 = {'fish': fish_n}
        query = "SELECT 魚貨名稱 AS Name,魚貨價格 AS Price FROM dbo.Fish WHERE "
        for i in range(0, len(Price_3['fish'])):
            query += "魚貨名稱 LIKE (N'%"+Price_3['fish'][i]+"%') "
            if i != len(Price_3['fish'])-1:
                query += "OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/recipe/normal/{num}')
async def get_Recipe_Normal(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    Request_N = {'num': num}
    if veg:
        veg_n = veg.split(',')
        Request_N['veg'] = veg_n
    if meat:
        meat_n = meat.split(',')
        Request_N['meat'] = meat_n
    if fish:
        fish_n = fish.split(',')
        Request_N['fish'] = fish_n
    query = "SELECT TOP " + \
        str(Request_N['num']) + \
        " 食譜名稱 AS Name,CONCAT(菜食材,',',肉食材,',',魚食材,',',其他食材) AS Ingredients,料理步驟 AS Step,圖片來源 AS IMGSource,ROUND(AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "Price3.魚貨價格"
    query += "),0) AS Price FROM dbo.RecipeNormal"
    if veg:
        query += " LEFT JOIN dbo.Veg  AS Price1 ON (作物名稱 LIKE CONCAT('%',dbo.RecipeNormal.菜食材,'%'))"
    if meat:
        query += " LEFT JOIN dbo.Meat AS Price2 ON (日期 = (SELECT TOP 1 日期 FROM dbo.Meat))"
    if fish:
        query += " LEFT JOIN dbo.Fish  AS Price3 ON (魚貨名稱 LIKE CONCAT('%',dbo.RecipeNormal.魚食材,'%'))"
    query += " WHERE "
    if veg:
        for i in range(0, len(Request_N['veg'])):
            query += "菜食材 LIKE (N'%"+Request_N['veg'][i]+"%') "
            if meat or fish or i != len(Request_N['veg'])-1:
                query += "OR "
    if meat:
        for j in range(0, len(Request_N['meat'])):
            query += "肉食材 LIKE (N'%"+Request_N['meat'][j]+"%') "
            if fish or j != len(Request_N['meat'])-1:
                query += "OR "
    if fish:
        for k in range(0, len(Request_N['fish'])):
            query += "魚食材 LIKE (N'%"+Request_N['fish'][k]+"%') "
            if k != len(Request_N['fish'])-1:
                query += "OR "
    query += "GROUP BY 食譜名稱,CONCAT(菜食材,',',肉食材,',',魚食材,',',其他食材),料理步驟,圖片來源 ORDER BY CASE WHEN AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "Price3.魚貨價格"
    query += ") IS NULL THEN 1 ELSE 0 END, AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "Price3.魚貨價格"
    query += ") ASC"
    df = pd.read_sql(query, cnxn)
    df = df.fillna('資料不足')

    query_r = "SELECT TOP " + \
        str(Request_N['num']) + \
        " 食譜名稱 AS Name, 菜食材 AS Ingredients1,肉食材 AS Ingredients2,魚食材 AS Ingredients3,其他食材 AS Ingredients4"
    query_r += " FROM dbo.RecipeNormal WHERE "
    for i in range(0, len(df['Name'])):
        query_r += "食譜名稱 LIKE (N'%"+df['Name'][i]+"%') "
        if i != len(df['Name'])-1:
            query_r += "OR "
    df_r = pd.read_sql(query_r, cnxn)

    for key in list(df_r['Ingredients1'].keys()):
        if not df_r['Ingredients1'].get(key):
            del df_r['Ingredients1'][key]
    for key in list(df_r['Ingredients2'].keys()):
        if not df_r['Ingredients2'].get(key):
            del df_r['Ingredients2'][key]
    for key in list(df_r['Ingredients3'].keys()):
        if not df_r['Ingredients3'].get(key):
            del df_r['Ingredients3'][key]
    for key in list(df_r['Ingredients4'].keys()):
        if not df_r['Ingredients4'].get(key):
            del df_r['Ingredients4'][key]
    for i in range(0, len(df_r['Ingredients1'])):
        df_r['Ingredients1'][i] = df_r['Ingredients1'][i].split(',')
    for i in range(0, len(df_r['Ingredients2'])):
        df_r['Ingredients2'][i] = df_r['Ingredients2'][i].split(',')
    for i in range(0, len(df_r['Ingredients3'])):
        df_r['Ingredients3'][i] = df_r['Ingredients3'][i].split(',')
    for i in range(0, len(df_r['Ingredients4'])):
        df_r['Ingredients4'][i] = df_r['Ingredients4'][i].split(',')

    query_veg = "SELECT 作物名稱 AS Name,平均價 AS Price FROM dbo.Veg WHERE "
    for i in range(0, len(df_r['Ingredients1'])):
        for j in range(0, len(df_r['Ingredients1'][i])):
            query_veg += "dbo.Veg.作物名稱 LIKE (N'%" + \
                df_r['Ingredients1'][i][j]+"%') OR "
    for i in range(0, len(df_r['Ingredients3'])):
        for j in range(0, len(df_r['Ingredients3'][i])):
            query_veg += "dbo.Veg.作物名稱 LIKE (N'%" + \
                df_r['Ingredients3'][i][j]+"%') OR "
    for i in range(0, len(df_r['Ingredients4'])):
        for j in range(0, len(df_r['Ingredients4'][i])):
            query_veg += "dbo.Veg.作物名稱 LIKE (N'%" + \
                df_r['Ingredients4'][i][j]+"%') OR "
            query_veg += "dbo.Veg.作物名稱 LIKE (N'%" + \
                df_r['Ingredients4'][i][j]+"%') "
            if (i != len(df_r['Ingredients4'])-1):
                query_veg += "OR "
            elif (j != len(df_r['Ingredients4'][i])-1):
                query_veg += "OR "
    query_veg += "ORDER BY 平均價 ASC"
    query_fish = "SELECT 魚貨名稱 AS Name, 魚貨價格 AS Price FROM dbo.Fish WHERE "
    for i in range(0, len(df_r['Ingredients1'])):
        for j in range(0, len(df_r['Ingredients1'][i])):
            query_fish += "dbo.Fish.魚貨名稱 LIKE (N'%" + \
                df_r['Ingredients1'][i][j]+"%') OR "
    for i in range(0, len(df_r['Ingredients3'])):
        for j in range(0, len(df_r['Ingredients3'][i])):
            query_fish += "dbo.Fish.魚貨名稱 LIKE (N'%" + \
                df_r['Ingredients3'][i][j]+"%') OR "
    for i in range(0, len(df_r['Ingredients4'])):
        for j in range(0, len(df_r['Ingredients4'][i])):
            query_fish += "dbo.Fish.魚貨名稱 LIKE (N'%" + \
                df_r['Ingredients4'][i][j]+"%') "
            if (i != len(df_r['Ingredients4'])-1):
                query_fish += "OR "
            elif (j != len(df_r['Ingredients4'][i])-1):
                query_fish += "OR "

    df_veg = pd.read_sql(query_veg, cnxn)
    df_fish = pd.read_sql(query_fish, cnxn)
    z = df_veg.copy()
    z.update(df_fish)
    z = z.to_dict('r')
    df = df.to_dict('r')
    df_fin = {}
    df_fin['Recipe'] = df
    df_fin['Detail'] = z
    return df_fin


@ app.get('/recipe/soup/{num}')
async def get_Recipe_Soup(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    Request_S = {'num': num}
    if veg:
        veg_s = veg.split(',')
        Request_S['veg'] = veg_s
    if meat:
        meat_s = meat.split(',')
        Request_S['meat'] = meat_s
    if fish:
        fish_s = fish.split(',')
        Request_S['fish'] = fish_s
    query = "SELECT TOP " + \
        str(Request_S['num']) + \
        " 食譜名稱 AS Name,CONCAT(菜食材,',',肉食材,',',魚食材,',',其他食材) AS Ingredients,料理步驟 AS Step,圖片來源 AS IMGSource,ROUND(AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "Price3.魚貨價格"
    query += "),0) AS Price FROM dbo.Recipe_Soup"
    if veg:
        query += " LEFT JOIN dbo.Veg  AS Price1 ON (作物名稱 LIKE CONCAT('%',dbo.Recipe_Soup.菜食材,'%'))"
    if meat:
        query += " LEFT JOIN dbo.Meat AS Price2 ON (日期 = (SELECT TOP 1 日期 FROM dbo.Meat))"
    if fish:
        query += " LEFT JOIN dbo.Fish  AS Price3 ON (魚貨名稱 LIKE CONCAT('%',dbo.Recipe_Soup.魚食材,'%'))"
    query += " WHERE "
    if veg:
        for i in range(0, len(Request_S['veg'])):
            query += "菜食材 LIKE (N'%"+Request_S['veg'][i]+"%') "
            if meat or fish or i != len(Request_S['meat'])-1:
                query += "OR "
    if meat:
        for j in range(0, len(Request_S['meat'])):
            query += "肉食材 LIKE (N'%"+Request_S['meat'][j]+"%') "
            if fish or j != len(Request_S['meat'])-1:
                query += "OR "
    if fish:
        for k in range(0, len(Request_S['fish'])):
            query += "魚食材 LIKE (N'%"+Request_S['fish'][k]+"%') "
            if k != len(Request_S['fish'])-1:
                query += "OR "
    query += "GROUP BY 食譜名稱,CONCAT(菜食材,',',肉食材,',',魚食材,',',其他食材),料理步驟,圖片來源 ORDER BY CASE WHEN AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "+Price3.魚貨價格"
    query += ") IS NULL THEN 1 ELSE 0 END, AVG("
    if veg:
        query += "Price1.平均價"
        if meat or fish:
            query += "+"
    if meat:
        query += "Price2."
        query += '"白肉雞(門市價高屏)"'
        if fish:
            query += "+"
    if fish:
        query += "Price3.魚貨價格"
    query += ") ASC"
    df = pd.read_sql(query, cnxn)
    df = df.fillna('資料不足')
    return df.to_dict('r')

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8000")
