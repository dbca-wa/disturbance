import traceback
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http.response import HttpResponse
from ledger.payments.utils import oracle_parser
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse

from disturbance.components.das_payments import reports
from disturbance.components.main.models import Region, District, Tenure, ApplicationType, ActivityMatrix, MapLayer, DASMapLayer, GlobalSettings
from disturbance.components.main.serializers import RegionSerializer, DistrictSerializer, TenureSerializer, \
    ApplicationTypeSerializer, ActivityMatrixSerializer, BookingSettlementReportSerializer, OracleSerializer, \
    MapLayerSerializer, DASMapLayerSerializer, GlobalSettingsSerializer
from django.core.exceptions import ValidationError

from disturbance.components.main.utils import handle_validation_error
from disturbance.helpers import is_internal, is_customer
from disturbance.settings import PAYMENT_SYSTEM_PREFIX


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all().order_by('id')
    serializer_class = DistrictSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.none() 
    serializer_class = RegionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return Region.objects.all().order_by('id')
        return Region.objects.none()


class ActivityMatrixViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = ActivityMatrix.objects.all().order_by('id')
    queryset = ActivityMatrix.objects.none()
    serializer_class = ActivityMatrixSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            # specific to Disturbance application, so only exposing one record (most recent)
            return [ActivityMatrix.objects.filter(name='Disturbance').order_by('-version').first()]
        return ActivityMatrix.objects.none()

#    def list(self, request, *args, **kwargs):
#        matrix = ActivityMatrix.objects.filter(name='Disturbance').order_by('-version').first()
#        return Response( [activity['children'][0] for activity in matrix.schema] )


class TenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenure.objects.all().order_by('order')
    serializer_class = TenureSerializer


class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = ApplicationType.objects.all().order_by('order')
    queryset = ApplicationType.objects.none()
    serializer_class = ApplicationTypeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return ApplicationType.objects.order_by('order').filter(visible=True)
        return ApplicationType.objects.none()

    @list_route(methods=['GET',])
    def searchable_application_types(self, request, *args, **kwargs):
        queryset = ApplicationType.objects.order_by('order').filter(visible=True, searchable=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class BookingSettlementReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "date":request.GET.get('date'),
            }
            serializer = BookingSettlementReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Settlement Report-{}'.format(str(serializer.validated_data['date']))
            # Generate Report
            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


def oracle_integration(date, override):
    system = PAYMENT_SYSTEM_PREFIX
    #oracle_codes = oracle_parser(date, system, 'Commercial Operator Licensing', override=override)
    # oracle_codes = oracle_parser(date, system, 'WildlifeCompliance', override=override)
    oracle_codes = oracle_parser(date, system, 'Apiary Licensing System', override=override)


class OracleJob(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        try:
            data = {
                "date":request.GET.get("date"),
                "override": request.GET.get("override")
            }
            serializer = OracleSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'),serializer.validated_data['override'])
            data = {'successful':True}
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
            # raise serializers.ValidationError(repr(e.error_dict)) if hasattr(e, 'error_dict') else serializers.ValidationError(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.none()
    serializer_class = MapLayerSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return MapLayer.objects.filter(option_for_internal=True)
        elif is_customer(self.request):
            return MapLayer.objects.filter(option_for_external=True)
        return MapLayer.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DASMapLayerViewSet(viewsets.ModelViewSet):
    queryset = DASMapLayer.objects.none()
    serializer_class = DASMapLayerSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return DASMapLayer.objects.filter(option_for_internal=True)
        elif is_customer(self.request):
            return DASMapLayer.objects.filter(option_for_external=True)
        return DASMapLayer.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class GlobalSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalSettings.objects.all().order_by('id')
    serializer_class = GlobalSettingsSerializer