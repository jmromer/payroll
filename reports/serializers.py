from rest_framework import serializers

from .models import TimeEntry


class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = (
            'date',
            'employee_id',
            'hours_worked',
            'job_group',
            'report_number',
        )


class PayrollReportSerializer:
    def __init__(self, dataframe):
        self._reports = [{
            'employeeId': row['employee_id'],
            'amountPaid': '${:,.2f}'.format(row['amount_paid']),
            'payPeriod': {
                'startDate': row['start_date'].date(),
                'endDate': row['end_date'].date(),
            }
        } for row in dataframe.to_dict(orient='records')]

    @property
    def data(self):
        return {'payrollReport': {'employeeReports': self._reports}}
