import configparser
from datetime import datetime
import psycopg2
from psycopg2 import OperationalError

config = configparser.ConfigParser()
config.read("config.ini")

database = config['DB']['database']
user_db = config['DB']['user_db']
password = config['DB']['password']
host = config['DB']['host']
port = config['DB']['port']


class UserDB:
    def create_connection(self, contacts_user):
        connection = None
        try:
            connection = psycopg2.connect(
                database=database,
                user=user_db,
                password=password,
                host=host,
                port=port
            )
            print('Connection to PosrgresQL DB successfull')
        except OperationalError as e:
            print(f"The error '{e}' occurred$$$$$$$$$$$$$$$$$$$")

        first_name = contacts_user['first_name']
        last_name = contacts_user['last_name']
        company = contacts_user['company']
        position = contacts_user['position']
        url_linkedin = contacts_user['url_linkedin']
        email = contacts_user['email']
        number_phone = contacts_user['number_phone']
        created_at = str(datetime.now())

        user_records = (
            first_name, last_name, company, position, url_linkedin, email, number_phone, created_at)
        new_contact = (
            f"INSERT INTO linkedin_users (first_name, last_name, company, position, url_linkedin, email, number_phone, created_at) VALUES {user_records}"
        )

        with connection:
            try:
                query = f"""SELECT * FROM linkedin_users WHERE first_name='{first_name}' AND last_name='{last_name}'"""
                cursor = connection.cursor()
                cursor.execute(query)
                check_contact = cursor.fetchall()

                if not check_contact:
                    cursor.execute(new_contact)
                    connection.commit()
                    user = True
                else:
                    print(f'This user exists already = ', contacts_user['first_name'])
                    user = False
            except Exception as e:
                print('User not added in db, error = ', e, '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

            return {'user': user}


class CheckUsersDB:
    def check_user_link(self, link):
        connection = None
        try:
            connection = psycopg2.connect(
                database=database,
                user=user_db,
                password=password,
                host=host,
                port=port
            )
            print('Connection to PosrgresQL DB successfull')
        except OperationalError as e:
            print(f"The error '{e}' occurred$$$$$$$$$$$$$$$$$$$")

        cursor = connection.cursor()

        with connection:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_users (
             id SERIAL PRIMARY KEY,
             first_name VARCHAR(254),
             last_name VARCHAR(254),
             company VARCHAR(254),
             position VARCHAR(254),
             url_linkedin VARCHAR(254),
             email VARCHAR(254),
             number_phone VARCHAR(254),
             created_at TIMESTAMP
           )
           """
                           )
            connection.commit()

        with connection:
            try:
                new_users_links = []
                query = f"""SELECT url_linkedin FROM linkedin_users"""
                cursor = connection.cursor()
                cursor.execute(query)
                check_contact = cursor.fetchall()
                new_check_contact = [(''.join(list(i))) for i in check_contact]
                print('111111111111111111111111111111111111111111111111111111111', new_check_contact)
                for i in link:
                    if i not in new_check_contact:
                        new_users_links.append(i)
            except Exception as e:
                print(f'Error  in DB {e} *******************************************************')
            return new_users_links
