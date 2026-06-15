import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def close():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
