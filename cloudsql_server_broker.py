from google.cloud.sql.connector import Connector
import sqlalchemy

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
        # Note: Saving credentials in environment variables is convenient, but not
        # secure - consider a more secure solution such as
        # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
        # keep secrets safe.
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

    def execute_query(self, query: str):
        """
        Executes a SQL query on the connected database.

        Args:
            query (str): The SQL query to be executed.
        Returns:
            sqlalchemy.engine.result.ResultProxy: The result of the query.
        """
        with self.__engine.connect() as conn:
            result = conn.execute(query)
        return result