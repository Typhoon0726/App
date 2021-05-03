import pyodbc
import pandas as pd
from fastapi import FastAPI
import py_functions
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=tcp:2021-report.database.windows.net,1433;Database=System;Uid={C107156216@o365.nkust.edu.tw};Pwd={Typhoon890726};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword')
cursor = cnxn.cursor()

origins = [
    "http://localhost:8000",
    "http://typhoon890726.ddns.net:8000",
    "http://typhoon200000726.ddns.net:8000",
    "http://61.62.207.113:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def get_data():
    df = py_functions.test_data(cnxn)
    return df.to_dict('r')


@app.get('/price/veg/{veg}')
async def get_Price_Veg(veg: str):
    veg_n = veg.split(',')
    Price_1 = {'veg': veg_n}
    df = py_functions.Price_Veg(cnxn, Price_1)
    return df


@app.get('/price/meat/{meat}')
async def get_Price_Meat(meat: str):
    meat_n = meat.split(',')
    Price_2 = {'meat': meat_n}
    df = py_functions.Price_Meat(cnxn, Price_2)
    return df


@app.get('/price/veg/{fish}')
async def get_Price_Fish(fish: str):
    fish_n = fish.split(',')
    Price_3 = {'fish': fish_n}
    df = py_functions.Price_Fish(cnxn, Price_3)
    return df


@app.get('/recipe/normal/{num}')
async def get_Recipe_Normal(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    veg_n = veg.split(',')
    meat_n = meat.split(',')
    fish_n = fish.split(',')
    Request_N = {'num': num, 'veg': veg_n, 'meat': meat_n, 'fish': fish_n}
    df = py_functions.Recipe_Normal(cnxn, Request_N)
    return df


@app.get('/recipe/soup/{num}')
async def get_Recipe_Soup(num: int, veg: Optional[str] = None, meat: Optional[str] = None, fish: Optional[str] = None):
    veg_s = veg.split(',')
    meat_s = meat.split(',')
    fish_s = fish.split(',')
    Request_S = {'num': num, 'veg': veg_s, 'meat': meat_s, 'fish': fish_s}
    df = py_functions.Recipe_Normal(cnxn, Request_S)
    return df

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8000")
