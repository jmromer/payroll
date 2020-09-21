import csv
from datetime import datetime as dt
from datetime import timedelta

import pandas as pd
from django.db import models
from django_pandas.managers import DataFrameManager

from .errors import AlreadyExistsError, AttachmentError


class JobGroup(models.Model):
    """Persistence model for job groups. Seed using ./manage.py db_seed."""
    name = models.CharField(max_length=128)
    hourly_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TimeEntry(models.Model):
    """Persistence model for an given time report entry."""
    report_number = models.IntegerField()
    date = models.DateField()
    hours_worked = models.FloatField()
    employee_id = models.IntegerField()
    job_group = models.ForeignKey(JobGroup, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'

    objects = DataFrameManager()

    @classmethod
    def last_updated_at(cls):
        try:
            return cls.objects.latest().created_at
        except cls.DoesNotExist:
            return None

    @classmethod
    def report_is_saved(cls, report_number):
        return cls.objects.filter(report_number=report_number).exists()

    @classmethod
    def create_from_csv(cls, csv_file):
        filename = csv_file.name

        # ensure attachment is a CSV file
        if not filename.endswith('.csv'):
            raise AttachmentError(f'File {filename} must be a CSV file.')

        # ensure attachment isn't too large
        if csv_file.multiple_chunks():
            raise AttachmentError(f'File {filename} is too large to process.')

        rep_number = filename.rstrip('.csv').split('-')[-1]

        # ensure the report hasn't already been persisted
        if cls.report_is_saved(rep_number):
            raise AlreadyExistsError(f'Report {rep_number} is already saved.')

        # parse and persist time entries
        csv_lines = csv_file.read().decode('utf8').splitlines()
        if len(csv_lines) < 2:
            raise AttachmentError(f'File {filename} contains no data.')

        header, *rows = csv_lines
        entries = csv.DictReader([header.replace(' ', '_'), *rows])

        for entry in entries:
            entry['job_group'] = JobGroup.objects.get(name=entry['job_group'])
            entry['date'] = dt.strptime(entry['date'], '%d/%m/%Y').date()
            TimeEntry.objects.create(report_number=rep_number, **entry)


class PayrollReport:
    @staticmethod
    def generate():
        """
        Generate a payroll report from all available TimeEntry data.
        Returns a Pandas DataFrame with bi-monthly aggregated pay records.
        """
        query = TimeEntry.objects.all().select_related('job_group')

        if not query.count():
            return pd.DataFrame()

        report_df = query.to_dataframe(index='id',
                                       fieldnames=(
                                           'employee_id',
                                           'date',
                                           'hours_worked',
                                           'job_group__hourly_rate',
                                       ))

        # convert pay date to datetime
        report_df['date'] = pd.to_datetime(report_df['date'])

        # compute amount paid
        report_df['amount_paid'] = report_df['hours_worked'] * report_df[
            'job_group__hourly_rate']

        report_df.drop(
            columns=['hours_worked', 'job_group__hourly_rate'],
            inplace=True,
        )

        # create two monthly bins: [1, 15], (15, EOM]
        semi_monthly = pd.Grouper(key='date', freq='SMS', closed='right')
        report_df = report_df.groupby(['employee_id',
                                       semi_monthly]).sum().reset_index()

        # set start date, reflecting the open left bound in second half of month
        report_df['start_date'] = report_df['date'].apply(
            lambda date: date + timedelta(days=1) if date.day == 15 else date)

        # set end date
        report_df['end_date'] = report_df['date'] + pd.offsets.SemiMonthEnd(1)
        del report_df['date']

        return report_df
