import psycopg2
import configparser
from datetime import datetime


class User(object):
    """ Corpus Table Utilities """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./db/functions/DBConfig.ini')
        self.host = config['PostgresDB']['host']
        self.port = config['PostgresDB']['port']
        self.database = config['PostgresDB']['database']
        self.user = config['PostgresDB']['user']
        self.password = config['PostgresDB']['password']

    def get_user_by_user_id(self, user_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_agg(row_to_json(t)) from 
                                (select u.id, u.user_name, u.password, u.active, u.groups from icaa.users u 
                                where id = %s and active = true) t
                            """
            cursor.execute(select_query, (user_id,))
            user_json = cursor.fetchall()
            connection.close()
            return user_json[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from user table", error)
    # endDef

    def get_user_by_user_name(self, user_name):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_agg(row_to_json(u.*)) from icaa.users u where user_name = %s and active = true"""
            cursor.execute(select_query, (user_name,))
            user_json = cursor.fetchall()
            connection.close()
            return user_json[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from user table", error)
    # endDef

    def insert_user(self, user_name, password, active='Y', groups='icaa_user'):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            date_timestamp = datetime.now()
            insert_query = """ INSERT INTO icaa.users (user_name, password, created_date, active, groups)
                         VALUES (%s, %s, %s, %s, %s)"""
            record_to_insert = (user_name, password, date_timestamp, active, groups)
            cursor.execute(insert_query, record_to_insert)
            connection.commit()
            connection.close()
            return_msg = "User created successfully "
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into users table", error)

    def delete_user(self, user_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            date_timestamp = datetime.now()
            delete_query = """ DELETE from icaa.users where id = %s"""
            cursor.execute(delete_query, (user_id,))
            connection.commit()
            connection.close()
            return_msg = "User deleted successfully "
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to delete record from users table", error)

    def update_password(self, user_id, new_password):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            update_query = """ UPDATE icaa.users SET password = %s where id = %s"""
            cursor.execute(update_query, (new_password, user_id))
            connection.commit()
            connection.close()
            return_msg = "Password updated successfully"
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to update password for users table", error)

    def update_group(self, user_id, new_group):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            update_query = """ UPDATE icaa.users SET groups = %s where id = %s"""
            cursor.execute(update_query, (new_group, user_id))
            connection.commit()
            connection.close()
            return_msg = "Group updated successfully"
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to update group in users table", error)
