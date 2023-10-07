from typing import Union
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT,
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:

                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result
    async def create_table_Users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE 
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_Users(self, full_name, username, telegram_id):
        sql = "INSERT INTO Users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_Users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_Users(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_Users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_Users_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_Users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", fetchrow=True)

    async def drop_Users(self):
        await self.execute("DROP TABLE Users", execute=True)

    async def see_Users(self, tg_id):
        sql = "SELECT * FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, tg_id, fetch=True)

#davomat
    async def create_table_davomat(self):
        sql = """
               CREATE TABLE IF NOT EXISTS DAVOMAT (
               id SERIAL PRIMARY KEY,
               Faculty VARCHAR(255) NOT NULL,
               Fullname VARCHAR (100) NOT NULL ,
               Davomat VARCHAR (100) NOT NULL ,
               Vaqti VARCHAR (100) NOT NULL,
               Tekshirdi VARCHAR (100) NOT NULL,
               telegram_id BIGINT NOT NULL   
               );
               """
        await self.execute(sql, execute=True)

    async def add_davomat(self, telegram_id, Fullname, Faculty, Davomat, Vaqti, Tekshirdi):
        sql = "INSERT INTO DAVOMAT (telegram_id, Fullname, Faculty, Davomat, Vaqti, Tekshirdi)" \
              " VALUES($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, telegram_id, Fullname, Faculty, Davomat, Vaqti, Tekshirdi, fetchrow=True)

    async def select_all_davomat(self):
        sql = "SELECT * FROM DAVOMAT"
        return await self.execute(sql, fetch=True)

    async def select_user_davomat(self, **kwargs):
        sql = "SELECT * FROM DAVOMAT WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users_davomat(self):
        sql = "SELECT COUNT(*) FROM DAVOMAT"
        return await self.execute(sql, fetchval=True)

    async def update_user_username_davomat(self, telegram_id, Fullname):
        sql = "UPDATE DAVOMAT SET telegram_id=$1 WHERE Fullname=$2"
        return await self.execute(sql, telegram_id, Fullname, execute=True)

    async def delete_users_davomat(self):
        await self.execute("DELETE FROM DAVOMAT WHERE TRUE", execute=True)

    async def drop_users_davomat(self):
        await self.execute("DROP TABLE DAVOMAT", execute=True)

    async def admin_TYUTOR(self, faculty):
        sql = "SELECT * FROM DAVOMAT WHERE faculty=$1"
        return await self.execute(sql, faculty, fetch=True)

######tyutorlar
    async def create_table_tyutor(self):
        sql = """
               CREATE TABLE IF NOT EXISTS tyutor (
               faculty VARCHAR(255) NOT NULL,
               fullname VARCHAR (100) NOT NULL ,
               telegram_id BIGINT NOT NULL   
               );
               """
        await self.execute(sql, execute=True)

    async def add_tyutor(self, telegram_id, fullname, faculty):
        sql = "INSERT INTO tyutor (telegram_id, fullname, faculty)" \
              " VALUES($1, $2, $3) returning *"
        return await self.execute(sql, telegram_id, fullname, faculty, fetchrow=True)

    async def select_all_tyutor(self):
        sql = "SELECT * FROM tyutor"
        return await self.execute(sql, fetch=True)

    async def select_user_tyutor(self, **kwargs):
        sql = "SELECT * FROM tyutor WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users_tyutor(self):
        sql = "SELECT COUNT(*) FROM tyutor"
        return await self.execute(sql, fetchval=True)

    async def update_user_username_tyutor(self, telegram_id, fullname):
        sql = "UPDATE tyutor SET telegram_id=$1 WHERE fullname=$2"
        return await self.execute(sql, telegram_id, fullname, execute=True)

    async def delete_users_tyutor(self):
        await self.execute("DELETE FROM tyutor WHERE TRUE", execute=True)

    async def drop_users_tyutor(self):
        await self.execute("DROP TABLE tyutor", execute=True)

    async def show_Tyutor(self, faculty):
        sql = "SELECT * FROM tyutor WHERE faculty=$1"
        return await self.execute(sql, faculty, fetch=True)

    async def show_Tyutor_name(self, name):
        sql = "SELECT * FROM tyutor WHERE fullname=$1"
        return await self.execute(sql, name, fetch=True)

    async def delete_db_tyutor(self, del_name):
        sql = "DELETE FROM tyutor WHERE fullname=$1"
        return await self.execute(sql, del_name, execute=True)