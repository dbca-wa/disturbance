""" This module provides generic end points for using with
    models that are registered with django reversion.

    Some methods will only work if the django apps are in
    the 'components' directory
"""
import sys
import logging
import datetime
import json

from deepdiff import DeepDiff
from django.apps import apps
from django.http import JsonResponse
from rest_framework import views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from reversion.models import Version

from disturbance.helpers import is_internal

logger = logging.getLogger(__name__)


class InternalAuthorizationView(views.APIView): # pylint: disable=too-many-ancestors
    """ This ViewSet adds authorization that only allows internal users to
        return data.
    """
    def get(self, request):
        """ Deny access to the version history for external users """
        if not is_internal(self.request):
            raise PermissionDenied()

class GetVersionsView(InternalAuthorizationView):
    """ A View to return all unique (no duplicated) versions of a model as .json """
    def get(self, request, app_label, component_name, model_name, pk, reference_id_field):
        """ Returns all versions for any model object

            api/history/app_label/component_name/model_name/pk/

            Example:

            api/history/disturbance/proposals/Proposal/1933/
        """
        super().get(self)

        logger.debug('app_label = %s', app_label)
        logger.debug('model_name = %s', model_name)
        logger.debug('pk = %s', pk)
        logger.debug('component_name =  %s', component_name)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.debug('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        revision_comment_filter = request.GET.get('revision_comment_filter')

        if revision_comment_filter:
            versions = Version.objects.get_for_object(instance).select_related('revision')\
            .filter(revision__comment__contains=revision_comment_filter).get_unique()
        else:
            versions = Version.objects.get_for_object(instance).select_related('revision')\
            .get_unique()

        logger.debug('versions %s', versions)

        # Build the list of versions
        versions_list = []
        for index, version in enumerate(versions):
            lodgement_number = f'{getattr(instance, reference_id_field)}-{index}'
            versions_list.append({
                'lodgement_number': lodgement_number,
                'processing_status': version.field_dict['processing_status'],
                'date_created': version.revision.date_created}
            )

        return Response(versions_list)

class GetVersionView(InternalAuthorizationView):
    """ Will return any serialized verison of any model using any serializer """
    def get(self, request, app_label, component_name, model_name, serializer_name, pk, \
        version_number):
        """ Returns a specific version of any model object

            api/history/app_label/component_name/model_name/serializer_name/pk/version_number/

            Example:

            api/history/disturbance/proposals/Proposal/InternalProposalSerializer/1933/0/

            0 is the most current versions
            1 is one version older
            2 is two older and so on...

        """
        super().get(self)

        logger.debug('app_label = %s', app_label)
        logger.debug('model_name = %s', model_name)
        logger.debug('pk = %s', pk)
        logger.debug('version_number =  %s', version_number)
        logger.debug('component_name =  %s', component_name)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.info('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        """ It's important that we always retrieve the full list of unique
            versions filtered by revision__comment

            If instead we try to get the version by index like so:

            Version.objects.get_for_object(instance)[int(newer_version)]

            We will have the wrong data because not all versions are 
            displayed on the front end, only those that are unique and
            have a processing_status revision comment
        """
        versions = list(Version.objects.get_for_object(instance).select_related('revision')\
            .filter(revision__comment__contains='processing_status').get_unique())

        version = versions[int(version_number)]

        model_class = instance.__class__

        serializer_class = getattr(
            sys.modules[f'{app_label}.components.{component_name}.serializers'],
            serializer_name)

        instance = model_class(**version.field_dict)

        serializer = serializer_class(instance,context={'request':request})

        return Response(serializer.data)

class GetCompareVersionsView(InternalAuthorizationView):
    """ Returns the difference between two specific versions of any model object

        api/history/compare/app_label/model_name/pk/newer_version/older_version/

        Example:

        api/history/compare/disturbance/Proposal/1933/0/1/

        0 is the most current versions
        1 is one version older
        2 is two older and so on...

        In practice the compare is much more complicated than the view as the data
        structure can be vastly different especially if it has JSON fields 
        therefor unless a model has only basic fields some model specific logic
        will need to be implimented in the appropriate component.

    """
    def get(self, request, app_label, model_name, pk, newer_version, older_version):
        """ Returns the difference between two specific versions of any model object """
        super().get(self)

        logger.debug('app_label = %s', app_label)
        logger.debug('model_name = %s', model_name)
        logger.debug('pk = %s', pk)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.debug('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        """ It's important that we always retrieve the full list of unique
            versions filtered by revision__comment

            If instead we try to get the version by index like so:

            Version.objects.get_for_object(instance)[int(newer_version)]

            We will have the wrong data because not all versions are 
            displayed on the front end, only those that are unique and
            have a processing_status revision comment
        """        
        versions = list(Version.objects.get_for_object(instance).select_related('revision')\
            .filter(revision__comment__contains='processing_status').get_unique())

        newer_version = versions[int(newer_version)]
        older_version = versions[int(older_version)]

        differences = DeepDiff(newer_version.field_dict, older_version.field_dict, \
                                ignore_order=True)

        default_mapping = {
            datetime.datetime: lambda d: str(d),
            datetime.date: lambda d: str(d)
        }

        #formatted_differences = json.dumps(json.loads(differences.to_json(
        #    default_mapping=default_mapping)), indent=4, sort_keys=True)

        formatted_differences = json.loads(differences.to_json(
            default_mapping=default_mapping))

        logger.debug('\n\nformatted_differences = %s \n\n', formatted_differences)              

        return JsonResponse(formatted_differences)

class GetCompareFieldVersionsView(InternalAuthorizationView):
    """ Returns the difference for a specific field
     between two specific versions of any model object

        api/history/compare/app_label/model_name/pk/newer_version/older_version/compare_field/

        Example:

        api/history/compare/disturbance/Proposal/1933/0/2/data/
        
        Takes an optional querystring (get) parameter: "differences_only"

        If ?differences_only=True is added then it will return only the
        older (less current) version differences.

    """
    def get(self, request, app_label, model_name, pk, newer_version, older_version, compare_field):
        """ Returns the difference between two specific versions of any model object """
        super().get(self)

        logger.debug('app_label = %s', app_label)
        logger.debug('model_name = %s', model_name)
        logger.debug('pk = %s', pk)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.debug('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        """ It's important that we always retrieve the full list of unique
            versions filtered by revision__comment

            If instead we try to get the version by index like so:

            Version.objects.get_for_object(instance)[int(newer_version)]

            We will have the wrong data because not all versions are 
            displayed on the front end, only those that are unique and
            have a processing_status revision comment
        """
        versions = list(Version.objects.get_for_object(instance).select_related('revision')\
            .filter(revision__comment__contains='processing_status').get_unique())

        newer_version = versions[int(newer_version)]
        older_version = versions[int(older_version)]

        logger.debug('\n\nnewer_version.field_dict[compare_field] = ' + str(newer_version.field_dict[compare_field]))
        logger.debug('\n\nnewer_version.field_dict[compare_field] = ' + str(older_version.field_dict[compare_field]))

        differences = DeepDiff(newer_version.field_dict[compare_field], older_version.field_dict[compare_field], ignore_order=True)

        differences_only = request.GET.get('differences_only')
        if differences_only:
            differences_list = []
            for difference in differences.items():
                if "values_changed" in difference:
                    for k, diff in difference[1].items():
                        differences_list.append({k.split('\'')[-2]:diff['new_value'],})
            return Response(differences_list)

        default_mapping = {
            datetime.datetime: lambda d: str(d),
            datetime.date: lambda d: str(d)
        }

        formatted_differences = json.loads(differences.to_json(
            default_mapping=default_mapping))

        logger.debug('\n\nformatted_differences = %s \n\n', formatted_differences)   

        return JsonResponse(formatted_differences)