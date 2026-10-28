import os
from django.core.files import File
import traceback

from disturbance.components.proposals.models import Proposal
from disturbance.helpers import is_internal as request_is_internal
    

def process_generic_document(request, instance, document_type=None, *args, **kwargs):
    print("process_generic_document")
    print(request.data)
    try:
        action = request.data.get('action')
        input_name = request.data.get('input_name')
        comms_log_id = request.data.get('comms_log_id')
        comms_instance = None

        if document_type == 'comms_log' and comms_log_id and comms_log_id != 'null':
            comms_instance = instance.comms_logs.get(id=comms_log_id)
        elif document_type == 'comms_log':
            comms_instance = instance.comms_logs.create()

        if action == 'list':
            pass
        elif action == 'delete':
            delete_document(request, instance, comms_instance, document_type, input_name)
        elif action == 'cancel':
            deleted = cancel_document(request, instance, comms_instance, document_type, input_name)
        elif action == 'save':
            save_document(request, instance, comms_instance, document_type, input_name)

        # HTTP Response varies by action and instance type
        if comms_instance and action == 'cancel' and deleted:
            return deleted
        elif comms_instance:
            returned_file_data = [dict(file=d._file.url, id=d.id, name=d.name,) for d in comms_instance.documents.all() if d._file]
            return {'filedata': returned_file_data, 'comms_instance_id': comms_instance.id}
        # example document_type
        elif input_name:
            if document_type == SupportingApplicationDocument.DOC_TYPE_NAME:
                documents_qs = instance.supporting_application_documents

            returned_file_data = [dict(file=d._file.url, id=d.id, name=d.name,) for d in documents_qs.filter(input_name=input_name) if d._file]
            return { 'filedata': returned_file_data }
        else:
            returned_file_data = [dict(file=d._file.url, id=d.id, name=d.name, ) for d in instance.documents.all() if d._file]
            return {'filedata': returned_file_data}

    except Exception as e:
        print(traceback.print_exc())
        raise e


def delete_document(request, instance, comms_instance, document_type, input_name=None):
    # example document_type
    if 'document_id' in request.data:
        if document_type == SupportingApplicationDocument.DOC_TYPE_NAME:
            document_id = request.data.get('document_id')
            document = instance.supporting_application_documents.get(id=document_id)

    # comms_log doc store delete
    elif comms_instance and 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = comms_instance.documents.get(id=document_id)

    # default doc store delete
    elif 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = instance.documents.get(id=document_id)

    if document._file and os.path.isfile(
            document._file.path):
        os.remove(document._file.path)

    if document:
        document.delete()


def cancel_document(request, instance, comms_instance, document_type, input_name=None):
        if document_type == SupportingApplicationDocument.DOC_TYPE_NAME:
            document_list = instance.supporting_application_documents.all()
        elif comms_instance:
            document_list = comms_instance.documents.all()
        else:
            document_list = instance.documents.all()

        for document in document_list:
            if document._file and os.path.isfile(document._file.path):
                os.remove(document._file.path)
            document.delete()

        if comms_instance:
            return comms_instance.delete()


def save_document(request, instance, comms_instance, document_type, input_name=None):
        # Match model related_name to instance or comms_instance, eg.
        # sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='documents')..
        # this document can be accessed or created by 'instance.documents'

        # example document_type
        if 'filename' in request.data and input_name:
            _file = request.data.get('_file')
            if _file is None:
                _file = request.FILES.get('_file')
            if _file is None:
                raise ValueError('An uploaded file is required.')
            filename = os.path.basename(_file.name)

            if document_type == SupportingApplicationDocument.DOC_TYPE_NAME:
                document = instance.supporting_application_documents.get_or_create(input_name=input_name, name=filename)[0]
            elif isinstance(instance, Proposal):
                document = instance.documents.get_or_create(input_name=input_name, name=filename)[0]
            else:
                raise ValueError('Object type is wrong')

            document._file = _file
            document.is_internal = request_is_internal(request)
            document.save()

        # comms_log doc store save
        elif comms_instance and 'filename' in request.data:
            _file = request.data.get('_file')
            if _file is None:
                _file = request.FILES.get('_file')
            if _file is None:
                raise ValueError('An uploaded file is required.')
            filename = os.path.basename(_file.name)

            document = comms_instance.documents.get_or_create(
                name=filename)[0]
            document._file = _file
            document.is_internal = request_is_internal(request)
            document.save()

        # default doc store save
        elif 'filename' in request.data:
            _file = request.data.get('_file')
            if _file is None:
                _file = request.FILES.get('_file')
            if _file is None:
                raise ValueError('An uploaded file is required.')
            filename = os.path.basename(_file.name)

            document = instance.documents.get_or_create(
                name=filename)[0]
            document._file = _file
            document.is_internal = request_is_internal(request)
            document.save()


# For transferring files from temp doc objs to comms_log objs
def save_comms_log_document_obj(request, instance, comms_instance, temp_document):
    document = comms_instance.documents.get_or_create(
        name=temp_document.name)[0]
    document.is_internal = request_is_internal(request)
    _save_document_copy(document, temp_document)

# For transferring files from temp doc objs to default doc objs
def save_default_document_obj(instance, temp_document):
    document = instance.documents.get_or_create(
        name=temp_document.name)[0]
    _save_document_copy(document, temp_document)


def _save_document_copy(document, temp_document):
    with temp_document._file.open('rb') as source:
        document._file = File(source, name=os.path.basename(temp_document._file.name))
        document.save()
