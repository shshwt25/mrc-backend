import psycopg2
import configparser
from datetime import datetime


class AppRolesCorpus(object):
    """ Corpus Table Utilities """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./db/functions/DBConfig.ini')
        self.host = config['PostgresDB']['host']
        self.port = config['PostgresDB']['port']
        self.database = config['PostgresDB']['database']
        self.user = config['PostgresDB']['user']
        self.password = config['PostgresDB']['password']

    def maintain_app_roles_corpus(self, app_role_id, corpus_id_list):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            print(corpus_id_list)

            if len(corpus_id_list) > 0:
                corpus_id_list_int = [int(i) for i in corpus_id_list.split(",")]
                print('Going to delete')
                # Delete the corpus records which is not available in the corpus_id_list if available
                delete_query = """ DELETE FROM icaa.app_roles_corpus 
                                    WHERE app_role_id = (%s) AND corpus_id NOT IN %s
                                """
                records_to_delete = (app_role_id, tuple(corpus_id_list_int))
                cursor.execute(delete_query, records_to_delete)
                connection.commit()
            else:
                delete_query = """ DELETE FROM icaa.app_roles_corpus 
                                                    WHERE app_role_id = (%s)
                                                """
                records_to_delete = (app_role_id,)
                cursor.execute(delete_query, records_to_delete)
                connection.commit()
                connection.close()
                return_msg = "Records updated successfully into app roles corpus table"
                return return_msg

            # Select the corpus ids for the input app role id
            select_query = """ SELECT ARRAY_AGG(corpus_id) FROM icaa.app_roles_corpus 
                                WHERE app_role_id = (%s) 
                            """

            cursor.execute(select_query, (app_role_id,))
            available_corpus_list = cursor.fetchall()[0][0]
            connection.commit()

            if available_corpus_list is None:
                available_corpus_list = []

            if corpus_id_list is not None:
                for corpus_id in corpus_id_list_int:
                    if corpus_id not in available_corpus_list:
                        print('Going to  insert', corpus_id)
                        date_timestamp = datetime.now()

                        insert_query = """ INSERT into icaa.app_roles_corpus (app_role_id, corpus_id, created_date)
                                            VALUES (%s, %s, %s)
                                                """
                        record_to_insert = (app_role_id, corpus_id, date_timestamp)
                        cursor.execute(insert_query, record_to_insert)
                        connection.commit()

            connection.close()
            return_msg = "Corpus associated successfully for selected role"
            return return_msg
        except (Exception, psycopg2.Error) as error:
            print("Failed to update records into app roles corpus table", error)

    # endDef

    def get_all_corpus_for_role(self, app_role_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_to_json(array_agg(row_to_json(t)))
                from (
                  select arc.corpus_id, c.corpus_name from icaa.app_roles_corpus arc , icaa.corpus c 
                  where arc.app_role_id = %s and arc.corpus_id = c.corpus_id
                  and c.active is true
                  order by arc.corpus_id
                ) t """
            cursor.execute(select_query, (app_role_id,))
            corpus_json = cursor.fetchall()
            connection.close()
            if corpus_json[0][0] is None:
                return_list = []
            else:
                return_list = corpus_json[0][0]
            return return_list
        except (Exception, psycopg2.Error) as error:
            print("Failed to select records from app roles corpus table", error)

    # endDef

    def get_all_roles_corpus(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.database)
            cursor = connection.cursor()
            select_query = """ select array_to_json(array_agg(row_to_json(t)))
                from (
                  select ar.app_role_id, ar.app_role_name, arc.corpus_id, c.corpus_name
                  from icaa.app_roles ar, icaa.app_roles_corpus arc, icaa.corpus c
                  where ar.app_role_id = arc.app_role_id and arc.corpus_id = c.corpus_id
				  and c.active is true
				  order by ar.app_role_id, arc.corpus_id
                ) t """
            cursor.execute(select_query)
            corpus_json = cursor.fetchall()
            connection.close()
            return corpus_json[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Failed to select all records from app roles corpus table", error)

    # endDef
