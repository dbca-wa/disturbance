import traceback
import base64
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django_countries import countries
from django.db.models.functions import Concat
from django.db.models import F, Value, CharField
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route,renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser,Address
from ledger.address.models import Country
from datetime import datetime,timedelta, date
from disturbance.components.organisations.models import  (   
                                    Organisation,
                                )

from disturbance.components.users.serializers import   (   
                                                UserSerializer,
                                                UserAddressSerializer,
                                                PersonalSerializer,
                                                ContactSerializer,
                                                UserFilterSerializer,

                                            )
from disturbance.helpers import is_customer, is_internal
#from disturbance.components.main.utils import retrieve_department_users

#class DepartmentUserList(views.APIView):
#    renderer_classes = [JSONRenderer,]
#    def get(self, request, format=None):
#        data = cache.get('department_users')
#        if not data:
#            retrieve_department_users()
#            data = cache.get('department_users')
#        return Response(data)
#        
#        serializer  = UserSerializer(request.user)

class GetCountries(views.APIView):
    renderer_classes = [JSONRenderer,]
    def get(self, request, format=None):
        country_list = []
        for country in list(countries):
            country_list.append({"name": country.name, "code": country.code})
        return Response(country_list)


class GetProfile(views.APIView):
    renderer_classes = [JSONRenderer,]
    def get(self, request, format=None):
        serializer  = UserSerializer(request.user,
                context={'request': request}
                )
        return Response(serializer.data)

from rest_framework import filters
#class UserListFilterView(generics.ListAPIView):
#    """ https://cop-internal.dbca.wa.gov.au/api/filtered_users?search=russell
#    """
#    queryset = EmailUser.objects.all()
#    serializer_class = UserFilterSerializer
#    filter_backends = (filters.SearchFilter,)
#    search_fields = ('email', 'first_name', 'last_name')


class UserViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.none()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return EmailUser.objects.all()
        elif is_customer(self.request):
            qs = EmailUser.objects.filter(Q(id=user.id))
            return qs
        return EmailUser.objects.none()

    @list_route(methods=['GET',])
    def get_department_users(self, request, *args, **kwargs):
        try:
            search_term = request.GET.get('term', '')
            #serializer = UserSerializer(
            #        staff,
            #        many=True
            #        )
            #return Response(serializer.data)
            data = self.get_queryset().filter(is_staff=True). \
                filter(Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)). \
                values('email', 'first_name', 'last_name')[:10]
            data_transform = [{'id': person['email'], 'text': person['first_name'] + ' ' + person['last_name']} for person in data]
            return Response({"results": data_transform})
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def update_personal(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PersonalSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_contact(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ContactSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    # @detail_route(methods=['POST',])
    # def update_address_orig(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         serializer = UserAddressSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         address, created = Address.objects.get_or_create(
    #             line1 = serializer.validated_data['line1'],
    #             locality = serializer.validated_data['locality'],
    #             state = serializer.validated_data['state'],
    #             country = serializer.validated_data['country'],
    #             postcode = serializer.validated_data['postcode'],
    #             user = instance 
    #         )
    #         instance.residential_address = address
    #         instance.save()
    #         serializer = UserSerializer(instance)
    #         return Response(serializer.data);
    #     except serializers.ValidationError:
    #         print(traceback.print_exc())
    #         raise
    #     except ValidationError as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(repr(e.error_dict))
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if instance.residential_address:
                address = Address.objects.filter(id=instance.residential_address.id)
                total_addresses=address.count()
                if total_addresses > 0:
                    residential_address = Address.objects.get(id=address[0].id) 
                    residential_address.locality=serializer.validated_data['locality']
                    residential_address.state=serializer.validated_data['state']
                    residential_address.country=serializer.validated_data['country']
                    residential_address.postcode=serializer.validated_data['postcode']
                    residential_address.line1=serializer.validated_data['line1']
                    residential_address.save()
                    instance.residential_address= residential_address
            else:
                address=Address.objects.create(
                    line1=serializer.validated_data['line1'],
                    locality=serializer.validated_data['locality'],
                    state=serializer.validated_data['state'],
                    country=serializer.validated_data['country'],
                    postcode=serializer.validated_data['postcode'],
                    user=instance
                )
                address.save()
                instance.residential_address = address
                instance.save()

            with transaction.atomic():
                instance.save()
                serializer = UserSerializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))



    @detail_route(methods=['POST',])
    def upload_id(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.upload_identification(request)
            with transaction.atomic():
                instance.save()
                instance.log_user_action(EmailUserAction.ACTION_ID_UPDATE.format(
                '{} {} ({})'.format(instance.first_name, instance.last_name, instance.email)), request)
            serializer = UserSerializer(instance, partial=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET', ])
    def pending_org_requests(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationRequestDTSerializer(
                instance.organisationrequest_set.filter(
                    status='with_assessor'),
                many=True,
                context={'request': request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
