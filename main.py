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
    query = "SELECT 作物名稱,平均價 FROM dbo.Veg WHERE 作物名稱 LIKE (N'%花椰%')"
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/price/veg/{veg}')
async def get_Price_Veg(veg: str):
    veg_n = veg.split(',')
    Price_1 = {'veg': veg_n}
    query = "SELECT 作物名稱,平均價 FROM dbo.Veg WHERE "
    for i in range(0, len(Price_1['veg'])):
        query += "作物名稱 LIKE (N'%"+Price_1['veg'][i]+"%') "
        if i != len(Price_1['veg'])-1:
            query += "OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/price/meat/{meat}')
async def get_Price_Meat(meat: str):
    meat_n = meat.split(',')
    Price_2 = {'meat': meat_n}
    query = "SELECT TOP 1 日期,"
    for i in range(0, len(Price_2['meat'])):
        if Price_2['meat'][i] == '雞肉':
            query += '"白肉雞(門市價高屏)"'
            if len(Price_2['meat']) >= 2 and i == 0:
                query += ","
        elif Price_2['meat'][i] == '雞蛋':
            query += '"雞蛋(產地)"'
            if len(Price_2['meat']) >= 2 and i == 0:
                query += ","
    query += " FROM dbo.Meat"
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/price/veg/{fish}')
async def get_Price_Fish(fish: str):
    fish_n = fish.split(',')
    Price_3 = {'fish': fish_n}
    query = "SELECT 魚貨名稱,平均價 FROM dbo.Fish WHERE "
    for i in range(0, len(Price_3['fish'])):
        query += "魚貨名稱 LIKE (N'%"+Price_3['fish'][i]+"%') "
        if i != len(Price_3['fish'])-1:
            query += "OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/recipe/normal/{num}')
async def get_Recipe_Normal(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    veg_n = veg.split(',')
    meat_n = meat.split(',')
    fish_n = fish.split(',')
    Request_N = {'num': num, 'veg': veg_n, 'meat': meat_n, 'fish': fish_n}
    query = "SELECT 食譜名稱,CONCAT(菜食材,',',肉食材,',',魚食材,',',其他食材) AS 食材,料理步驟,圖片來源,Price1.平均價 AS 菜食材價格 FROM dbo.RecipeNormal LEFT JOIN dbo.Veg  AS Price1 ON (dbo.Veg.作物名稱 LIKE CONCAT('%',dbo.RecipeNormal.菜食材,'%')) LEFT JOIN dbo.Recipe WHERE "
    for i in range(0, len(Request_N['veg'])):
        query += "菜食材 LIKE (N'%"+Request_N['veg'][i]+"%') OR "
    for j in range(0, len(Request_N['meat'])):
        query += "肉食材 LIKE (N'%"+Request_N['meat'][j]+"%') OR "
    for k in range(0, len(Request_N['fish'])):
        query += "魚食材 LIKE (N'%"+Request_N['fish'][k]+"%') "
        if k != len(Request_N['fish'])-1:
            query += "OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')


@app.get('/recipe/soup/{num}')
async def get_Recipe_Soup(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    veg_s = veg.split(',')
    meat_s = meat.split(',')
    fish_s = fish.split(',')
    Request_S = {'num': num, 'veg': veg_s, 'meat': meat_s, 'fish': fish_s}
    query = "SELECT 食譜名稱,料理步驟,圖片來源 FROM dbo.RecipeSoup WHERE "
    for i in range(0, len(Request_S['veg'])):
        query = query + "菜食材 LIKE (N'%"+Request_S['veg'][i]+"%') OR "
    for j in range(0, len(Request_S['meat'])):
        query = query + "肉食材 LIKE (N'%"+Request_S['meat'][j]+"%') OR "
    for k in range(0, len(Request_S['fish'])):
        query = query + "魚食材 LIKE (N'%"+Request_S['fish'][k]+"%') "
        if k != len(Request_S['fish'])-1:
            query = query+"OR "
    df = pd.read_sql(query, cnxn)
    return df.to_dict('r')

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8000")
