import pytest

from .models import JobGroup, TimeEntry


@pytest.mark.django_db
def test_payroll_report_with_no_time_entries(client):
    resp = client.get('/payroll-report/')
    assert resp.status_code == 404
    assert 'No data to report' in resp.data['error']


@pytest.mark.django_db
def test_payroll_report_with_time_entries(client, time_entries):
    resp = client.get('/payroll-report/')
    assert resp.status_code == 200
    entries = resp.data.get('payrollReport', {}).get('employeeReports', {})
    assert len(entries) > 0


@pytest.mark.django_db
def test_time_entries_with_valid_csv(post_csv_file, job_groups):
    """Respond with 201 if the given report is succesfully processed."""
    resp = post_csv_file('/time-entries/', 'time-report-42.csv')
    assert resp.status_code == 201
    assert resp.data is None


@pytest.mark.django_db
def test_time_entries_with_persisted_report(post_csv_file, job_groups):
    """Respond with 405 if the given report has already been processed."""
    resp = post_csv_file('/time-entries/', 'time-report-42.csv')
    assert resp.status_code == 201

    resp = post_csv_file('/time-entries/', 'time-report-42.csv')
    assert resp.status_code == 405
    assert 'is already saved' in resp.data['error']


@pytest.mark.django_db
def test_time_entries_with_empty_file(post_csv_file):
    """Respond with 422 if the given report is empty."""
    resp = post_csv_file('/time-entries/', 'time-report-43.csv')
    assert resp.status_code == 422
    assert 'contains no data' in resp.data['error']
