import boto3
from boto3 import Session


class SessionManager:

    def create_session(self) -> Session:
        """Create session

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        :return:
        """
        session: Session = boto3.Session(profile_name='dev')
        # session = boto3.Session(
        #     aws_access_key_id=ACCESS_KEY,
        #     aws_secret_access_key=SECRET_KEY,
        #     aws_session_token=SESSION_TOKEN)
        return session
