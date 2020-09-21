from django.core.cache import cache
from django.utils.timezone import now
from rest_framework import parsers, status, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .errors import AlreadyExistsError, AttachmentError
from .models import PayrollReport, TimeEntry
from .serializers import PayrollReportSerializer


class PayrollReportViewSet(viewsets.ViewSet):
    def list(self, _request):
        """
        Retrieve a payroll report generated from all available time log data.
        Use a cached report if a valid cache entry is found.
        """
        report = cache.get('payroll_report')
        mru_dt = TimeEntry.last_updated_at()

        if not mru_dt:
            message = {'error': 'No data to report.'}
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        if not report or mru_dt > report['generated_at']:
            report_df = PayrollReport.generate()
            serializer = PayrollReportSerializer(report_df)
            report = {'generated_at': now(), 'data': serializer.data}
            cache.set('payroll_report', report)

        return Response(report['data'])


class TimeEntryViewSet(viewsets.ViewSet):
    parser_classes = (parsers.FileUploadParser, )

    def create(self, request):
        """
        Parse the given CSV attachment and persist each entry.
        """
        try:
            csv_file = request.FILES['file']
            TimeEntry.create_from_csv(csv_file)
        except (ParseError, AttachmentError) as err:
            return Response({'error': str(err)},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except AlreadyExistsError as err:
            return Response({'error': str(err)},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as err:
            return Response({'error': str(err)},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(None, status=status.HTTP_201_CREATED)
