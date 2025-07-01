import warnings
from collections import OrderedDict

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import parse_apps_and_model_labels
from django.db import DEFAULT_DB_ALIAS, router


class ProxyModelWarning(Warning):
    pass


class Command(BaseCommand):
    '''
        ## Create JSON Fixture from Masterlist related models
        Check the Admin --> ProposalType records to find the latest-1 (penultimate version of the latest ProposalType)) and update the adhoc_dumpdata.py script with that records PK

        ```
        # FROM das-test
        ./manage_ds.py adhoc_dumpdata > media/pt.json

        # Copy to destination environment (copy-paste from https://das-test-internal.dbca.wa.gov.au/media/pt.json)
        vi /folder/pt_das-test_05Jun2024.json

        ```

        ## Update to new PK
        vi /folder/pt_das-test_05Jun2024.json

        1. check latest version in Admin: (proposal_type_pk: 25, version 16, replaced_by 15_ 
           https://das-test-internal.dbca.wa.gov.au/ledger/admin/disturbance/proposaltype/
              --> proposal_type pk 25 (https://das-test-internal.dbca.wa.gov.au/ledger/admin/disturbance/proposaltype/25/change/)
              --> replaced_by will then be 25
              --> next version will be 17

        1. disturbance.proposaltype PK --> 30, say
        2. disturbance.proposaltype version --> 30, say
        3. :%s/proposal_type": 20/proposal_type": 30/g

        ## Update destination DB
        ### From shell clear existing records (Assuming these will/should not be not present in a new/fresh DAS PROD)
        QuestionOption.objects.all().delete()
        SectionQuestion.objects.all().delete()
        ProposalTypeSection.objects.all().delete()
        MasterlistQuestion.objects.all().delete()

        SpatialQueryQuestion.objects.all().delete()
        SpatialQueryLayer.objects.all().delete()
        SpatialQueryMetrics.objects.all().delete()
        DASMapLayer.objects.all().delete()
        CddpQuestionGroup.objects.all().delete()
        GlobalSettings.objects.all().delete()

        ### Load data to destination DB
        ```
        ./manage_ds.py loaddata disturbance/utils/csv/pt_das-test_05Jun2024.json
        ```

    '''
    help = (
        "Output the contents of the database as a fixture of the given format "
        "(using each model's default manager unless --all is specified)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label[.ModelName]', nargs='*',
            help='Restricts dumped data to the specified app_label or app_label.ModelName.',
        )
        parser.add_argument(
            '--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.',
        )
        parser.add_argument(
            '--indent', default=None, dest='indent', type=int,
            help='Specifies the indent level to use when pretty-printing output.',
        )
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a specific database to dump fixtures from. '
                 'Defaults to the "default" database.',
        )
        parser.add_argument(
            '-e', '--exclude', dest='exclude', action='append', default=[],
            help='An app_label or app_label.ModelName to exclude '
                 '(use multiple --exclude to exclude multiple apps/models).',
        )
        parser.add_argument(
            '--natural-foreign', action='store_true', dest='use_natural_foreign_keys', default=False,
            help='Use natural foreign keys if they are available.',
        )
        parser.add_argument(
            '--natural-primary', action='store_true', dest='use_natural_primary_keys', default=False,
            help='Use natural primary keys if they are available.',
        )
        parser.add_argument(
            '-a', '--all', action='store_true', dest='use_base_manager', default=False,
            help="Use Django's base manager to dump all models stored in the database, "
                 "including those that would otherwise be filtered or modified by a custom manager.",
        )
        parser.add_argument(
            '--pks', dest='primary_keys',
            help="Only dump objects with given primary keys. Accepts a comma-separated "
                 "list of keys. This option only works when you specify one model.",
        )
        parser.add_argument(
            '-o', '--output', default=None, dest='output',
            help='Specifies file to which the output is written.'
        )

    def handle(self, *app_labels, **options):
        format = options['format']
        indent = options['indent']
        using = options['database']
        excludes = options['exclude']
        output = options['output']
        show_traceback = options['traceback']
        use_natural_foreign_keys = options['use_natural_foreign_keys']
        use_natural_primary_keys = options['use_natural_primary_keys']
        use_base_manager = options['use_base_manager']
        pks = options['primary_keys']

        if pks:
            primary_keys = [pk.strip() for pk in pks.split(',')]
        else:
            primary_keys = []

        excluded_models, excluded_apps = parse_apps_and_model_labels(excludes)

        if len(app_labels) == 0:
            if primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict(
                (app_config, None) for app_config in apps.get_app_configs()
                if app_config.models_module is not None and app_config not in excluded_apps
            )
        else:
            if len(app_labels) > 1 and primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict()
            for label in app_labels:
                try:
                    app_label, model_label = label.split('.')
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    try:
                        model = app_config.get_model(model_label)
                    except LookupError:
                        raise CommandError("Unknown model: %s.%s" % (app_label, model_label))

                    app_list_value = app_list.setdefault(app_config, [])

                    # We may have previously seen a "all-models" request for
                    # this app (no model qualifier was given). In this case
                    # there is no need adding specific models to the list.
                    if app_list_value is not None:
                        if model not in app_list_value:
                            app_list_value.append(model)
                except ValueError:
                    if primary_keys:
                        raise CommandError("You can only use --pks option with one model")
                    # This is just an app - no model qualifier
                    app_label = label
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    app_list[app_config] = None

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            try:
                serializers.get_serializer(format)
            except serializers.SerializerDoesNotExist:
                pass

            raise CommandError("Unknown serialization format: %s" % format)
 
        def get_objects(count_only=False):
            from itertools import chain
            from disturbance.components.proposals.models import ProposalType, ProposalTypeSection, QuestionOption, SectionQuestion, MasterlistQuestion
            # Assuming 19 is the current pk of proposal_type on das_uat for Ecological Thinning. 
            pk_proposal_type = 19
            qs1 = ProposalType.objects.filter(pk=pk_proposal_type)
            qs2 = SectionQuestion.objects.filter(section__proposal_type__pk=pk_proposal_type)
            qs3 = ProposalTypeSection.objects.filter(proposal_type__id=pk_proposal_type)
            qs4 = QuestionOption.objects.filter()
            qs5 = MasterlistQuestion.objects.filter()              

            yield from chain(qs1, qs2, qs3, qs4, qs5)


        try:
            self.stdout.ending = None
            progress_output = None
            object_count = 0
            # If dumpdata is outputting to stdout, there is no way to display progress
            if (output and self.stdout.isatty() and options['verbosity'] > 0):
                progress_output = self.stdout
                object_count = sum(get_objects(count_only=True))
            stream = open(output, 'w') if output else None
            try:
                serializers.serialize(
                    format, get_objects(), indent=indent,
                    use_natural_foreign_keys=use_natural_foreign_keys,
                    use_natural_primary_keys=use_natural_primary_keys,
                    stream=stream or self.stdout, progress_output=progress_output,
                    object_count=object_count,
                )
            finally:
                if stream:
                    stream.close()
        except Exception as e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)
