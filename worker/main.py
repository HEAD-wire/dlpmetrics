import argparse
import os, sys
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.engine import URL
from pkg.util import genv, create_engine_from_env
from sqlalchemy.orm import Session
from pkg.models import Download

def download():
    pass

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))


if __name__ == '__main__':
    engine = create_engine_from_env()

    with Session(engine) as session:

        #TODO get all metrics