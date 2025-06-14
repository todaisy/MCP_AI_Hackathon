from dataclasses import dataclass, field
import datetime
import psycopg2 as psy


@dataclass
class User:
    user_id: int
    add_date: datetime.datetime = field(default_factory=datetime.datetime.now)
    g_docs: str = ''
    g_calendar: str = ''
    g_sheets: str = ''
    task_tracker: str = ''

    async def start(self, conn: psy.extensions.connection):
        with conn.cursor() as cur:
            cur.execute('SELECT user_id FROM users_db WHERE user_id = %s', (self.user_id,))
            if not cur.fetchone():
                cur.execute(
                    'INSERT INTO users_db (user_id, add_date) VALUES (%s, %s)',
                    (self.user_id, self.add_date)
                )
            conn.commit()

    async def add_any(self, conn: psy.extensions.connection, column_name: str):
        try:
            # Проверяем, есть ли атрибут у объекта
            value = getattr(self, column_name)

            # Допустимые колонки (защита от SQL-инъекций)
            allowed_columns = {'g_docs', 'g_calendar', 'g_sheets', 'task_tracker',}
            if column_name not in allowed_columns:
                raise ValueError(f"Недопустимое имя колонки: {column_name}")

            query = f"UPDATE users_db SET {column_name} = %s WHERE user_id = %s"

            with conn.cursor() as cur:
                cur.execute(query, (value, self.user_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка в add_any: {e}")
            return False

@dataclass
class Handlers:
    id: int
    user_id: int
    id_mess_input: str
    time_input: datetime.datetime = datetime.datetime.now()
    id_mess_output: str = ''
    time_output: datetime.datetime = datetime.datetime.now()
    correct: bool = True
    def do_request(self, conn: psy.extensions.connection):
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO handlers_db (user_id, id_mess_input) VALUES (%s, %s)',
                (self.user_id, self.id_mess_input)
            )
        conn.commit()

    def do_change_to_request(self, conn: psy.extensions.connection, ):
        with conn.cursor() as cur:
            cur.execute(
            "UPDATE handlers_db SET id_mess_output = %s,time_output = %s,correct = %s WHERE id = %s",
                ( self.id_mess_output,self.time_output,self.correct ,self.id )
            )
        conn.commit()


