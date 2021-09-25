import psycopg2
import configparser
from datetime import datetime


class AppRoles(object):
    """ App Roles Table Utilities """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./db/functions/DBConfig.ini')
        self.host = config['PostgresDB']['host']
        self.port = config['PostgresDB']['port']
        self.database = config['PostgresDB']['database']
        self.user = config['PostgresDB']['user']
        self.password = config['PostgresDB']['password']

    def insert_app_role(self, app_role_name):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            date_timestamp = datetime.now()
            insert_query = """ INSERT INTO icaa.app_roles (app_role_name, created_date)
                         VALUES (%s, %s)"""
            record_to_insert = (app_role_name,date_timestamp)
            cursor.execute(insert_query, record_to_insert)
            connection.commit()
            connection.close()
            return_msg = "Role created successfully"
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into app roles table", error)

    # endDef

    def get_roles_list(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_to_json(array_agg(row_to_json(t)))
                from (
                  select * from icaa.app_roles 
                ) t """
            cursor.execute(select_query)
            roles_json = cursor.fetchall()
            connection.close()
            return roles_json[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from app roles table", error)

    # endDef

    def get_role_by_role_id(self, app_role_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_to_json(array_agg(row_to_json(t)))
                from (
                  select * from icaa.app_roles where app_role_id = %s
                ) t """
            cursor.execute(select_query, (app_role_id,))
            roles_json = cursor.fetchall()
            connection.close()
            return roles_json[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from app roles table", error)

    # endDef


    def delete_app_role_by_id(self, app_role_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            delete_query = """ DELETE from icaa.app_roles where app_role_id = %s """
            cursor.execute(delete_query, (app_role_id,))
            connection.commit()
            connection.close()

            return_msg = "Role deleted successfully "
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to delete record from app roles table", error)
