# coding: utf-8
'''
Code for getting availability datq from Oslo City Bike.
We store the data in mongoDB.
'''
import os
import requests
from pymongo import MongoClient
from time import sleep 
import logging
import click
from dotenv import load_dotenv

sleepMinutes = 5 # time to sleep between every data retrieval.

def retreiveAvailability(clientIdentifier):
    headers = {"Client-Identifier": clientIdentifier}
    urlAvailability = 'https://oslobysykkel.no/api/v1/stations/availability'
    availability = requests.get(urlAvailability, headers=headers)
    return availability

def writeToOcbDatabaseAvailability(data):
    '''Write to mongodb.'''
    client = MongoClient('localhost', 27017)
    db = client.ocbDatabase
    collection = db.availability
    collection.insert_one(data)
    client.close()


@click.command()
def main():
    '''Code for getting availability datq from Oslo City Bike.
    We store the data in a mongoDB.
    '''
    logger = logging.getLogger(__name__)
    logger.info('Starting main function')

    clientId = os.environ.get('OCB_CLIENT_IDENTIFIER')

    sleepSeconds = sleepMinutes * 60
    while True:
        logger.info('Retrieving data from Oslo City Bike')
        availability = retreiveAvailability(clientId)
        if availability.ok == False:
            logger.info('Problems reading: ' + str(availability.status_code))
            sleep(sleepSeconds)
            continue
    
        logger.info('Storing to DB')
        writeToOcbDatabaseAvailability(availability.json())
        sleep(sleepSeconds)


if __name__ == '__main__':
    # Logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='retrieveData.log', level=logging.INFO, 
            format=log_fmt)

    # Source .env
    dotFile = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotFile)

    main()
