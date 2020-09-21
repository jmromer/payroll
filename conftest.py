import pytest

from reports.models import JobGroup, TimeEntry


@pytest.fixture
def post_csv_file(client):
    def wrapped(abspath, filename):
        return client.post(
            abspath,
            content_type='text/csv',
            data=open(f'./fixtures/{filename}', 'r').read(),
            HTTP_CONTENT_DISPOSITION=f'attachment; filename={filename}')

    return wrapped


@pytest.fixture
def job_groups():
    return [
        JobGroup.objects.create(name='A', hourly_rate=20),
        JobGroup.objects.create(name='B', hourly_rate=30)
    ]


@pytest.fixture
def time_entries(job_groups):
    entries = [
        {
            'report_number': 45,
            'date': '2016-10-15',
            'hours_worked': 7.5,
            'employee_id': 1,
            'job_group': job_groups[0]
        },
        {
            'report_number': 45,
            'date': '2016-10-20',
            'hours_worked': 4,
            'employee_id': 1,
            'job_group': job_groups[0]
        },
    ]
    for attrs in entries:
        TimeEntry.objects.create(**attrs)
