import pandas as pd


def test_data(cnxn):
    query = "SELECT 作物名稱,平均價 FROM dbo.Veg WHERE 作物名稱 LIKE (N'%花椰%')"
    df = pd.read_sql(query, cnxn)
    return df


def Price_Veg(cnxn, Price_1):
    query = "SELECT 作物名稱,平均價 FROM dbo.Veg WHERE "
    for i in range(0, len(Price_1['veg'])):
        query += "作物名稱 LIKE (N'%"+Price_1['veg'][i]+"%') "
        if i != len(Price_1['veg'])-1:
            query += "OR "
    df = pd.read_sql(query, cnxn)
    return df


def Price_Meat(cnxn, Price_2):
    query = "SELECT "
    for i in range(0, len(Price_2['meat'])):
        if Price_2['meat'][i] == '雞肉':
            query += "白肉雞(門市價高屏)"
            if len(Price_2['meat']) >= 2:
                query += ","
        elif Price_2['meat'][i] == '雞蛋':
            query += "雞蛋(產地)"
    query += " FROM dbo.Meat LIMIT 1"
    df = pd.read_sql(query, cnxn)
    return df


def Price_Fish(cnxn, Price_1):
    query = "SELECT 魚貨名稱,平均價 FROM dbo.Fish WHERE "
    for i in range(0, len(Price_1['fish'])):
        query += "魚貨名稱 LIKE (N'%"+Price_1['fish'][i]+"%') "
        if i != len(Price_1['veg'])-1:
            query += "OR "
    df = pd.read_sql(query, cnxn)
    return df


def Recipe_Normal(cnxn, Request_N):
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
    return df


def Recipe_Soup(cnxn, Request_S):
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
    return df
