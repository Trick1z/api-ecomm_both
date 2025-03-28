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
    connector = mysql.connector.connect(
        host='host.docker.internal',
        user='root',
        database='e-comm'
    )

    # localhost
    # connector = mysql.connector.connect(
    #     host='localhost',
    #     user='root',
    #     database='e-comm'
    # )

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


@app.post('/register.user/{role}')
def register_user(item: register, role: str):
    ticket_res = services.get_ticket(item.password, item.c_password)
    time_now = services.get_date()

    if ticket_res:

        hash_pw = services.hash(item.password)
        try:
            res = query.post(
                f"INSERT INTO user (username, email, password,role) VALUES ('{item.username}','{item.email}','{hash_pw}','{role}')")
            res_id = res['lastId']

            res2 = query.post(f"INSERT INTO cart (user_id) VALUES ({res_id});")

            return {"account": "accout has been added!",
                    "cart": "cart has been added!",

                    'msg': [res, res2]}
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
    username: str
    password: str


@app.post('/login.user')
def user_login(data: loginform):
    try:
        pw = services.hash(data.password)

        conn = get_DB()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM user WHERE username = '{data.username}' AND password = '{pw}'")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return {'msg': "user not found!", 'status': 500, }
        else:
            user_name = data.username
            return {'user': user_name, 'status': 200, "body": rows}
        # return res
    except Exception as err:
        return {'msg': err}
        # return {'msg': err,'status': status}


class addProducts (BaseModel):
    products_name: str
    products_desc: str
    category_id: int
    products_price: float
    stock_quantity: int
    img_url: str


@app.post('/post.products/')
def post_products(item: addProducts):

    try:
        res = query.post(
            f"INSERT INTO products (products_name,products_desc,products_price,stock_quantity,category_id) VALUES ('{item.products_name}','{item.products_desc}',{item.products_price},{item.stock_quantity},{item.category_id})")
        res_id = res['lastId']

        res2 = query.post(
            f"INSERT INTO img (img_url,products_id) VALUES ('{item.img_url}',{res_id})")

        print(res2)
        return {'products_msg': 'product has been added',
                'img_mag': 'img has been added',
                'status': 200
                }
    except Exception as err:
        return


@app.get('/get.{table}')
def get_data(table: str):
    try:
        res = query.get(f"SELECT * FROM {table} WHERE del_frag = 'N'")

        return res
    except Exception as err:
        return {'msg': err,
                'status': 500}


@app.get('/get.{table}/{id}')
def get_data(table: str, id: int):
    try:
        res = query.get(
            f"SELECT * FROM {table} WHERE del_frag = 'N' AND {table}_id = {id}")

        return res
    except Exception as err:
        return {'msg': err,
                'status': 500}


class sta_cat (BaseModel):
    name: str
    desc: str


@app.post('/post.{table}')
def post_category_status(table: str, data: sta_cat):

    try:
        res = query.post(
            f"INSERT INTO {table} ({table}_name,{table}_desc) VALUES ('{data.name}','{data.desc}')")
        return res
    except Exception as err:
        return {'msg': err}


@app.put('/delete.{table}/{id}')
def delete(table: str, id: int):
    try:
        res = query.put(
            f"UPDATE {table} SET del_frag = 'Y' WHERE {table}_id = {id};")
        return res
    except Exception as err:
        return {'msg': err}


@app.put('/delete2.img/{id}')
def delete(id: int):
    try:
        res = query.put(
            f"UPDATE img SET del_frag = 'Y' WHERE products_id = {id};")
        return res
    except Exception as err:
        return {'msg': err}


@app.put('/delete2.products/{id}')
def delete(id: int):
    try:
        res = query.put(
            f"UPDATE products SET del_frag = 'Y' WHERE products_id = {id};")
        return res
    except Exception as err:
        return {'msg': err}


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
def get_img_id(id: int):
    try:

        res = query.get(
            f"SELECT * FROM img WHERE del_frag = 'N' AND products_id = {id}")
        return res
    except Exception as err:
        return err


class editProducts (BaseModel):
    products_id: int
    products_name: str
    products_desc: str
    category_id: int
    products_price: float
    stock_quantity: int
    img_url: str


@app.put('/put.product_img')
def put_pro_img(item: editProducts):
    try:
        res = query.put(f"""UPDATE products SET products_name = '{item.products_name}',
                        products_desc = '{item.products_desc}',category_id = {item.category_id}, 
                        products_price = {item.products_price} , stock_quantity = {item.stock_quantity}
                        WHERE products_id = {item.products_id};""")

        res2 = query.put(f"""
                         UPDATE img SET img_url = '{item.img_url}' WHERE products_id = {item.products_id}
                         """)
        return {'product': res,
                'img-product': res2
                }
    except Exception as err:
        return


@app.get('/get_cart/{id}')
def get_cartId_userId(id: int):
    try:
        res = query.get(f"SELECT * FROM cart WHERE user_id = {id}")
        return {'msg': res}
    except Exception as err:
        return {'msg': err}


@app.get('/get_cart_item/{id}')
def get_cartId_userId(id: int):
    try:
        res = query.get(
            f"SELECT * FROM cart_item WHERE cart_id = {id} AND del_frag ='N'")
        return {'msg': res}
    except Exception as err:
        return {'msg': err}


class cart(BaseModel):
    products_id: int
    cart_id: int
    quantity: int


@app.post('/cart_post.cartItem')
def post_order_item(item: cart):
    time = services.get_date()
    try:
        res = query.post(
            f"INSERT INTO cart_item (cart_id,products_id,quantity,added_at) VALUES ({item.cart_id},{item.products_id},{item.quantity},'{time}');")

        return {'msg': res}
    except Exception as err:
        return {'msg': err}


@app.get('/get_cart_count/{id}')
def get_cart_count(id: int):
    try:
        res = query.get(
            f"SELECT COUNT(*) AS cart_items FROM cart_item WHERE cart_id = {id} AND del_frag = 'N'; ")

        return {'msg': res}
    except Exception as err:
        return {'msg': err}


class order(BaseModel):
    products_data: list
    user_id: int
    amount_total: float


@app.post('/order_order_item')
def post_orders(item: order):
    time = services.get_date()
    status_id = 1

    try:
        res = query.post(
            f"INSERT INTO orders (user_id, order_date, status_id, total_amount) VALUES ({item.user_id},'{time}',{status_id},{item.amount_total})",)

        res_id = res['lastId']

        print(res_id)
        # order Id Here

        res_cart = []
        res_order = []

        for each in item.products_data:
            cart_id = each['cart_item_id']
            res_putCart = query.put(
                f"UPDATE cart_item SET del_frag = 'Y' WHERE cart_item_id = {cart_id}")

            p_id = each['products_data']['products_id']
            quantity = each['quantity']
            price = each['products_data']['products_price']

            res_orderItem = query.post(
                f"INSERT INTO order_item (order_id,products_id,quantity,price) VALUES ({res_id},{p_id},{quantity},{price})")

            res_cart.append(res_putCart)
            res_order.append(res_orderItem)

        return {'Add order': res,
                'change state': res_cart,
                'orderItem': res_order}

        return {'Add order': 'test',
                }

    except Exception as err:
        return {'msg': err}


@app.get('/get_orders/')
def get_order_admin():
    try:
        res = query.get(f"""
                        SELECT
                        order_id,
                        order_date,
                        total_amount,
                        u.username,
                        s.status_name as status
                        FROM
                        orders o
                        INNER JOIN user u ON o.user_id = u.user_id
                        INNER JOIN status s ON o.status_id = s.status_id 
                        """)
        return res

    except Exception as e:
        return e


class editFrom (BaseModel):
    id: int
    name: str
    desc: str


@app.put('/edit.put/{table}={id}')
def edt_cat_sta(table: str, id: int, data: editFrom):
    try:
        res = query.put(
            f"UPDATE {table} SET {table}_name = '{data.name}' , {table}_desc = '{data.desc}' WHERE {table}_id = {id}")
        return res
    except Exception as e:
        return e




@app.put('/put_orders_status/{o_id}={statusID}')
def put_ord_sta(o_id: int, statusID: int):

    try:
        res = query.put(
            f"UPDATE orders SET status_id = {statusID} WHERE order_id = {o_id}")
        return res
    except Exception as e:
        return e




@app.get('/get_order_userID/{id}')
def get_odr_userID(id: int):
    try:
        res = query.get(f"""
                        SELECT
                            o.order_date,
                            o.order_id,
                            o.total_amount,
                            s.status_name
                           
                        FROM
                            orders o
                            INNER JOIN USER u ON o.user_id = u.user_id
                            INNER JOIN STATUS s ON o.status_id = s.status_id
                        WHERE o.user_id = {id}
                        """)
        return res
    except Exception as e:
        return e

# @app.put('/cancel.user.order')
# def cancel_order():
#     try:
#         res = query.put(f"UPDATE orders SET")
#         return
#     except Exception as e:
#         return e


@app.get('/orders.item/ref={id}')
def get_ord_item(id: int):
    try:
        res = query.get(f"""
                        SELECT
                            p.products_name,
                            p.products_desc,
                            o.quantity,
                            o.price ,
                            i.img_url
                        FROM
                            order_item o
                        INNER JOIN products p ON o.products_id = p.products_id
                        INNER JOIN img i ON o.products_id = i.img_id 
                        WHERE
                            o.order_id = {id}
                        """)
        return res
    except Exception as e:
        return e
