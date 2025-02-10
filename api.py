from typing import Union
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, File, Response, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import base64
from dateutil import parser
import pytz
import io
import csv
from openpyxl import load_workbook
import hashlib
from bs4 import BeautifulSoup

load_dotenv()


# get DB
def get_DB():
    # deploy docker
    # connector = mysql.connector.connect(
    #     host='host.docker.internal',
    #     user='root',
    #     database='mydb'
    # )

    # localhost
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        database='e-com'
    )

    return connector


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class gettime():
#     def time():
#         time =
#         return


class query():
    def get(order: String):
        try:
            conn = get_DB()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(order)
            data = cursor.fetchall()

            cursor.close()
            conn.close()

            if not data:
                return None
            else:
                return {
                    'msg': 200,
                    'data': data
                }

        except Exception as err:
            return {'msg': err, }

    def post(order: String):
        try:
            conn = get_DB()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(order)
            conn.commit()
            
            id = cursor.lastrowid
            cursor.close()
            conn.close()

            return {'msg': "your data been added !",
                    'status': 200,
                    'lastId': id
                    }

        except Exception as err:
            return {'msg': err, }
    

    def put(order: String):
        try:
            cnx = get_DB()
            cursor = cnx.cursor()
            cursor.execute(order)
            cnx.commit()
            cursor.close()
            cnx.close()

            return {
                'msg': 'Success',
                'status': 200
            }
        except Exception as err:
            return {'msg': err, }


# gettime ex. 2025-02-08 15:53:13

class services():
    def get_last_insert_id():
        try:
            result = query.get("SELECT last_insert_rowid() FROM ori")
            return result[0]['last_insert_rowid()'] if result else None
        except Exception as err:
            print(f"Error getting last insert ID: {err}")
            return None



    def get_date():
        now = datetime.now()
        mysql_datetime = now.strftime('%Y-%m-%d %H:%M:%S')

        return mysql_datetime

    def get_ticket(pw: str, c_pw: str):

        if pw == c_pw:
            return True
        else:
            return False

    def hash(data: str) -> str:
        hashed = hashlib.sha256(data.encode()).hexdigest()
        truncated_hash = hashed[:16]
        formatted_hash = f"0x{truncated_hash.upper()}"
        return formatted_hash


#   try:
#     return
# except Exception as err:
#     return {'msg':err}

# model
class register(BaseModel):
    username: str
    email: str
    password: str
    c_password: str


@app.post('/register.user')
def register_user(item: register):
    ticket_res = services.get_ticket(item.password, item.c_password)
    time_now = services.get_date()

    if ticket_res:

        hash_pw = services.hash(item.password)
        try:
            res = query.post(
                f"INSERT INTO user (username, email, password,create_date) VALUES ('{item.username}','{item.email}','{hash_pw}','{time_now}')")
            return res
        except Exception as err:
            return {'msg': err,
                    'status': status}
    else:
        return {
            'msg': 'password not match!',
            'status': 500
        }


# login by get
class loginform(BaseModel):
    username:str
    password:str
    
@app.post('/login.user')
def user_login(data : loginform):
    try:
        pw = services.hash(data.password)
        
        conn = get_DB()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user WHERE username = '{data.username}' AND password = '{pw}'")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            return {'msg': "user not found!",'status': 500,}
        else:
            user_name = data.username
            return {'user':user_name,'status':200,"body":rows}
        # return res
    except Exception as err:
            return {'msg': err}
            # return {'msg': err,'status': status}
            
        
        
class addProducts (BaseModel):
    products_name:str
    products_desc:str
    category_id:int
    products_price:float
    stock_quantity:int
    img_url:str
@app.post('/post.products/')
def post_products(item:addProducts):
    
    time = services.get_date()
    try:
        res = query.post(f"INSERT INTO products (products_name,products_desc,products_price,stock_quantity,create_date,category_id) VALUES ('{item.products_name}','{item.products_desc}',{item.products_price},{item.stock_quantity},'{time}',{item.category_id})")
        res_id = res['lastId']
        
        
        res2 = query.post(f"INSERT INTO img (img_url,products_id) VALUES ('{item.img_url}',{res_id})")     
        
        
        print(res2)    
        return {'products_msg': 'product has been added',
                'img_mag': 'img has been added',
                'status': 200
                }
    except Exception as err:
        return        


@app.get('/get.{table}')
def get_data(table:str):
        try:
            res = query.get(f"SELECT * FROM {table} WHERE del_frag = 'N'")
            
            return res
        except Exception as err:
            return {'msg': err,
                    'status': 500}  
             
@app.get('/get.{table}/{id}')
def get_data(table:str,id:int):
        try:
            res = query.get(f"SELECT * FROM {table} WHERE del_frag = 'N' AND {table}_id = {id}")
            
            return res
        except Exception as err:
            return {'msg': err,
                    'status': 500}   
            
            
            
class sta_cat (BaseModel):
    name:str
    desc:str
    
@app.post('/post.{table}')
def post_category_status(table:str,data:sta_cat):
    
    try:
        res = query.post(f"INSERT INTO {table} ({table}_name,{table}_desc) VALUES ('{data.name}','{data.desc}')")
        return res
    except Exception as err:
        return  {'msg':err}  
    
    
    
@app.put('/delete.{table}/{id}')
def delete(table:str,id:int):
    try:
        res = query.put(f"UPDATE {table} SET del_frag = 'Y' WHERE {table}_id = {id};")
        return res
    except Exception as err:
        return  {'msg':err} 
    
    
@app.put('/delete2.img/{id}')
def delete(id:int):
    try:
        res = query.put(f"UPDATE img SET del_frag = 'Y' WHERE products_id = {id};")
        return res
    except Exception as err:
        return  {'msg':err}
     
@app.put('/delete2.products/{id}')
def delete(id:int):
    try:
        res = query.put(f"UPDATE products SET del_frag = 'Y' WHERE products_id = {id};")
        return res
    except Exception as err:
        return  {'msg':err} 
    
    
        
# @app.get('/get.product/')
# def get_product():
#     try:
        
#         res = query.get(f"SELECT * FROM products WHERE del_frag = 'N'")
#         return {'msg': res}
#     except Exception as err:
#         return {'msg': err,
#                 'status': 500}
        
        
# # class product_img_id (BaseModel):
# #     product : list
# @app.get('/get.product.img/')
# def get_product(): 
#     try:      
#         res = query.get(f"SELECT * FROM img WHERE del_frag = 'N'")
#         return {'msg': res}
#     except Exception as err:
#         return {'msg': err,
#                 'status': 500}

@app.get('/get_this_img/{id}')
def get_img_id(id:int):
    try:
        
        res = query.get(f"SELECT * FROM img WHERE del_frag = 'N' AND products_id = {id}")
        return res
    except Exception as err:
        return err
    
class editProducts (BaseModel):
    products_id:int
    products_name:str
    products_desc:str
    category_id:int
    products_price:float
    stock_quantity:int
    img_url:str
@app.put('/put.product_img')
def put_pro_img(item:editProducts):
    try:
        res = query.put(f"""UPDATE products SET products_name = '{item.products_name}',
                        products_desc = '{item.products_desc}',category_id = {item.category_id}, 
                        products_price = {item.products_price} , stock_quantity = {item.stock_quantity}
                        WHERE products_id = {item.products_id};""")
         
        res2 = query.put(f"""
                         UPDATE img SET img_url = '{item.img_url}' WHERE products_id = {item.products_id}
                         """)
        return {'product':res,
                'img-product':res2
                }
    except Exception as err:
        return
    