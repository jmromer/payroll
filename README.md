Payroll
=======

An API exposing two endpoints:

1. POST `/time-entries`:
   Accepts a CSV attachment conforming to the following format, which is parsed
   and persisted:

   ```csv
    date,hours worked,employee id,job group
    15/11/2016,7.5,1,A
    16/11/2016,7.5,1,B
    9/11/2016,4,2,B
   ```
   Duplicates are rejected.

2. GET `/payroll-report`:
   Retrieves a payroll report generated from all persisted time report data.

Dependencies
------------

- Python 3.8.0
- Postgres 12.4
- Redis 5.0.5
- Django REST Framework 3.11.1
- Pandas 1.1.2
- Pytest 6.0.2

Setup
-----

A `.tool-versions` file is provided in case ASDF version manager is used. To
install any missing versions, issue

```
asdf install
```

To install Python dependencies, create a virtualenv and install dependencies
with

```
pip install -r requirements.txt
```

Issue `bin/setup` from the project root to create a PostgreSQL database, migrate
it, and seed it with job groups.

Tests
-----

A minimal set of integration tests written with pytest are included in
`reports/tests.py`. See `requests.http` for a REST client log.

```
% pytest
================================== test session starts ===================================
collected 5 items

reports/tests.py .....                                                             [100%]

=================================== 5 passed in 0.78s ====================================

```

Walkthrough
-----------

### Routes

```py
# reports/urls.py L8-18 (080bbf84)

router.register(
    r'payroll-report',
    views.PayrollReportViewSet,
    basename='payroll-report',
)

router.register(
    r'time-entries',
    views.TimeEntryViewSet,
    basename='time-entries',
)
```

### Views

```py
# reports/views.py L12-54 (080bbf84)

class PayrollReportViewSet(viewsets.ViewSet):
    def list(self, _request):
        """
        Retrieve a payroll report generated from all available time log data.
        Use a cached report if a valid cache entry is found.
        """
        # . . .


class TimeEntryViewSet(viewsets.ViewSet):
    parser_classes = (parsers.FileUploadParser, )

    def create(self, request):
        """
        Parse the given CSV attachment and persist each entry.
        """
        # . . .
```

### Models

```py
# reports/models.py L12-123 (080bbf84)

class JobGroup(models.Model):
    """Persistence model for job groups. Seed using ./manage.py db_seed."""
    # . . .

class TimeEntry(models.Model):
    """Persistence model for an given time report entry."""
    # . . .

class PayrollReport:
    @staticmethod
    def generate():
        """
        Generate a payroll report from all available TimeEntry data.
        Returns a Pandas DataFrame with bi-monthly aggregated pay records.
        """
        # . . .
```
