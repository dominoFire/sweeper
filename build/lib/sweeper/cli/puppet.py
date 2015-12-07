__author__ = '@dominofire'

import click
import logging
import os
import sys
import sweeper.utils as utils

from sweeper.scheduler import execute_workflow, profile_workflow


def validate_yaml():
    descriptor_path = os.path.join(os.getcwd(), 'workflow.yaml')

    if not os.path.exists(descriptor_path):
        click.echo('workflow.yaml file in current directory not found')
        sys.exit(2)

    return descriptor_path


def configure_log():
    logging.basicConfig(filename='workflow.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())


def csv_path(descriptor_path):
    base, file, ext = utils.split_path(descriptor_path)
    gantt_csv_path = utils.join_path(base, '{}_gantt-data'.format(file), '.csv')

    return gantt_csv_path


@click.group()
def cli():
    """
    Workflow execution on cloud computing environments
    """
    click.echo('Sweeper says hello!')
    click.echo('Working dir: {}'.format(os.getcwd()))


@cli.command()
def run():
    configure_log()
    descriptor_path = validate_yaml()
    gantt_csv_path = csv_path(descriptor_path)

    execute_workflow(descriptor_path, gantt_csv_path)

    click.echo('Gantt data saved in {}'.format(gantt_csv_path))


@cli.command()
def profile():
    configure_log()
    descriptor_path = validate_yaml()
    gantt_csv_path = csv_path(descriptor_path)

    profile_workflow(descriptor_path, gantt_csv_path)

    click.echo('Gantt data saved in {}'.format(gantt_csv_path))


@cli.command()
def init():
    configure_log()
    descriptor_path = validate_yaml()

    click.echo('Coming soon...')
