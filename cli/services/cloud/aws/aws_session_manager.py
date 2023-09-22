import boto3
from boto3 import Session


class AwsSessionManager():

    def __init__(self):
        self.__session = None

    def create_session(self, region, profile, key, secret) -> Session:
        """Create session

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        :return:
        """

        if profile is not None:
            self.__session: Session = boto3.Session(region_name=region, profile_name=profile)
        elif key is not None and secret is not None:
            self.__session: Session = boto3.Session(region_name=region, aws_access_key_id=key,
                                                    aws_secret_access_key=secret)
        else:
            self.__session: Session = boto3.Session()

        return self.__session

    @property
    def session(self):
        return self.__session

    def close_session(self):
        self.__session.client().close()
