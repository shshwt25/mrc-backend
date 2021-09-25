import psycopg2
import configparser
from datetime import datetime


class AppRolesUsers(object):
    """ Roles Users Table Utilities """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./db/functions/DBConfig.ini')
        self.host = config['PostgresDB']['host']
        self.port = config['PostgresDB']['port']
        self.database = config['PostgresDB']['database']
        self.user = config['PostgresDB']['user']
        self.password = config['PostgresDB']['password']

    def maintain_app_roles_users(self, user_id, roles_id_list):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            print(roles_id_list)

            if len(roles_id_list) > 0:
                roles_id_list_int = [int(i) for i in roles_id_list.split(",")]
                print('Going to delete')
                # Delete the roles records which is not available in the roles_id_list if available
                delete_query = """ DELETE FROM icaa.app_roles_users 
                                    WHERE user_id = (%s) AND app_role_id NOT IN %s
                                """
                records_to_delete = (user_id, tuple(roles_id_list_int))
                cursor.execute(delete_query, records_to_delete)
                connection.commit()
            else:
                delete_query = """ DELETE FROM icaa.app_roles_users 
                                                    WHERE user_id = (%s)
                                                """
                records_to_delete = (user_id,)
                cursor.execute(delete_query, records_to_delete)
                connection.commit()
                connection.close()
                return_msg = "Records updated successfully into app roles users table"
                return return_msg

            # Select the roles ids for the input user id
            select_query = """ SELECT ARRAY_AGG(app_role_id) FROM icaa.app_roles_users 
                                WHERE user_id = (%s) 
                            """

            cursor.execute(select_query, (user_id,))
            available_roles_list = cursor.fetchall()[0][0]
            connection.commit()

            if available_roles_list is None:
                available_roles_list = []

            if roles_id_list is not None:
                for role_id in roles_id_list_int:
                    if role_id not in available_roles_list:
                        print('Going to  insert', role_id)
                        date_timestamp = datetime.now()

                        insert_query = """ INSERT into icaa.app_roles_users (app_role_id, user_id, created_date)
                                            VALUES (%s, %s, %s)
                                                """
                        record_to_insert = (role_id, user_id, date_timestamp)
                        cursor.execute(insert_query, record_to_insert)
                        connection.commit()

            connection.close()
            return_msg = "Records updated successfully into app roles users table"
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to update records into app roles users table", error)

    # endDef

    def get_all_roles_for_user_id(self, user_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_to_json(array_agg(row_to_json(t)))
                from (
                  select aru.user_id, aru.app_role_id, ar.app_role_name 
                  from icaa.app_roles_users aru , icaa.users u, icaa.app_roles ar 
                  where u.id = %s and aru.user_id = u.id and ar.app_role_id = aru.app_role_id
                  and u.active is true
                  order by aru.app_role_id
                ) t """
            cursor.execute(select_query, (user_id,))
            roles_json = cursor.fetchall()
            connection.close()
            if roles_json[0][0] is None:
                return_list = []
            else:
                return_list = roles_json[0][0]
            return return_list
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from app roles users table", error)

    # endDef
