from google.cloud.sql.connector import Connector
import sqlalchemy

from datetime import datetime

class cloudsql_server_broker:
    def __init__(self, project_id, region, instance_name, user, pswd, db_name):
        self.__instance_connection_name = f"{project_id}:{region}:{instance_name}"
        self.__db_user = user
        self.__db_pass = pswd
        self.__db_name = db_name
        self.__engine = self.connect_with_connector()

    def connect_with_connector(self) -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of MySQL. 

        Uses the Cloud SQL Python Connector package.
        """
        connector = Connector()

        # function to return the database connection object
        def getconn():
            conn = connector.connect(
                self.__instance_connection_name,
                "pytds",
                user=self.__db_user,
                password=self.__db_pass,
                db=self.__db_name
            )
            return conn

        # create connection pool with 'creator' argument to our connection object function
        pool = sqlalchemy.create_engine(
            "mssql+pytds://",
            creator=getconn,
        )
        return pool

    def execute_query(self, query: str, values):
        """
        Executes a SQL query on the connected database.

        Args:
            query (str): The SQL query to be executed.
        Returns:
            sqlalchemy.engine.result.ResultProxy: The result of the query.
        """
        with self.__engine.connect() as conn:
            if not values:
                result = conn.execute(query)
            else:
                result = conn.execute(query, values)
            conn.commit()
            conn.close()
        return result
    
    def write_to_player_prop_table(self, player_name, prop_type, sportsbook, line, over_odds, under_odds, timestamp):
        """
        Writes data to the 'player_prop_table' table in the 'bullybot_api_database' database.

        Args:
            player_name (str): The name of the player (varchar(50)).
            prop_type (str): The type of bet proposition (varchar(50)).
            sportsbook (str): The sportsbook (varchar(50)).
            line (float): The over line (decimal(18, 1)).
            over_odds (int): The over odds (int).
            under_odds (int): The under odds (int).
            timestamp (datetime): The timestamp of the data entry (datetime).
        """
        query = """
        INSERT INTO player_prop_table (player_name, prop_type, sportsbook, line, over_odds, under_odds, timestamp)
        VALUES (:player_name, :prop_type, :sportsbook, :line, :over_odds, :under_odds, :timestamp)
        """
        values = {
            'player_name': player_name,
            'prop_type': prop_type,
            'sportsbook': sportsbook,
            'line': line,
            'over_odds': over_odds,
            'under_odds': under_odds,
            'timestamp': timestamp
        }
        self.execute_query(sqlalchemy.text(query), values)