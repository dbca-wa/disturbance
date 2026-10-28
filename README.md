[![Build
status](https://travis-ci.org/dbca-wa/disturbance.svg?branch=master)](https://travis-ci.org/dbca-wa/disturbance/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/disturbance/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/disturbance?branch=master)
# Disturbance

The Disturbance Approval System (DAS) is used for by external approved organisations to submit applications for works that will potentially create a public disturbance. It is a database-backed Django application, using REST API with Vue.js as the client side app.


# Requirements

- Python (3.7.x)
- PostgreSQL (>=9.3)

Python library requirements should be installed using `pip`:

`pip install -r requirements.txt`

# Shapefile upload filenames

Upload `.shp`, `.shx`, `.dbf` and `.prj` components with the same original
basename. Proposal map uploads retain that original display name, but store
the components under a shared `proposalmapdocument_<uuid>` basename with
lowercase extensions. Upload order does not matter; unrelated documents keep
their independently generated filenames. Existing stored paths are not renamed.

Previously uploaded sets whose components were independently renamed must be
removed and uploaded again. When replacing a previously submitted (hidden)
set, hide all its components before uploading the replacement. Incomplete
sets are reported without deleting the uploaded components. GDAL conversion
failures are logged with their diagnostic output.

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    SECRET_KEY='thisismysecret'
    DATABASE_URL='postgis://USER:PASSWORD@HOST:PORT/DB_NAME'
    ALLOWED_HOSTS=[u'das.domain.com.au',u'das-internal.domain.com.au']
    EMAIL_HOST='EMAIL_HOST'
    BPOINT_USERNAME='BPOINT_USER'
    BPOINT_PASSWORD='BPOINT_PW'
    BPOINT_BILLER_CODE='123456'
    BPOINT_MERCHANT_NUM='987654'
    BPAY_BILLER_CODE='121212'
    CMS_URL="https://url-used-to-retrieve-system-id-via-api/"
    LEDGER_USER="UserForSystemIdAPI"
    LEDGER_PASS="Password"
    OSCAR_SHOP_NAME='Shop 1'
    DEFAULT_FROM_EMAIL='system@email_address.com.au'
    NOTIFICATION_EMAIL='user.notification@email_address.com.au'
    NON_PROD_EMAIL='user_1@email_address.com.au,user_2@email_address.com.au'
    EMAIL_INSTANCE='DEV/TEST/UAT/PROD'
    PRODUCTION_EMAIL=False
    BPAY_ALLOWED=False
    LEDGER_GST=10
    SITE_PREFIX='das'
    SITE_DOMAIN='domain.com.au
    TENURE_SECTION="Section1-0"
    SUPERVISOR_STOP_CMD="supervisorctl stop disturbance-uat"

### Content Security Policy

`django-csp` 4.x adds CSP headers to Django responses, including redirects and
production errors. Configure policies in `disturbance/settings.py`.

- **Enforced policy:** blocks plugins, external base URLs, and framing. It does
  not yet restrict scripts, styles, images, connections, or form submissions.
- **Report-only policy:** logs stricter policy violations in the browser console
  without blocking resources. No report collection endpoint is configured.

Check login, maps, payments, and admin workflows before enforcing stricter rules.
Verify both CSP headers on normal pages, redirects, and 404 responses:

```sh
curl -sS -D - -o /dev/null https://das-seg-dev.dbca.wa.gov.au/was_404_check
```

Proxy-generated responses and external SSO services need their own CSP configuration.

#### Application Schema

The application schema describes the fields that will be shown in the application questionaire, under the "Enter
Details" heading. This is in the JSON format and must, at the highest level, contain a list of sections, each with
their own set of fields (although a section is a type of field itself in this paradigm). These can be further nested
into groups of fields if required. A very simple example is shown below.

```
[
    {
        "type": "section", 
        "name": "section_1", 
        "label": "Section 1"
        "children": [
            {
                "type": "text", 
                "name": "name", 
                "label": "Provide you name"
            }, 
            {
                "type": "file", 
                "name": "qualification_attachments", 
                "label": "Qualification Attachment(s)"
            }, 
            {
                "type": "declaration", 
                "name": "acknowledgement", 
                "label": "I acknowledge that all this information is true"
            } 
        ]
    },
    {
        "type": "section", 
        "name": "section_2", 
        "label": "Section 2"
        "children": [
            {
                "type": "text", 
                "name": "additional_info", 
                "label": "Provide relevant additional information"
            },
            {
                "type": "declaration", 
                "name": "acknowledgement", 
                "label": "I acknowledge that all this information is true"
            } 
        ]
    }
]
```

##### Mandatory Attributes

All fields, including sections and groups, must at minimum contain three attributes: `type`, `name`, and `label`.

`type` is generally for html input types, except in a few cases, such as `section`, `group`, and `label`. The available
types are:

* `section` - base section for grouping fields
* `group` - nested group of fields within section or other groups
* `text` - standard text input
* `text_area` - large text input
* `number` - number input
* `date` - date input
* `select` - combo box input
* `radiobuttons` - radio button group input
* `checkbox` - single checkbox input
* `label` - just text-based label (usually goes before series of checkboxes)
* `file`- file input
* `declaration` - checkbox with declaration text next to it.
* `species` - special species lookup input

`name` is a field for identifying each field in the system. **Note: every field must have a totally unique name**. This
means no two fields anywhere in one application schema can have have the same name. Also note that the name cannot
contain spaces or special characters such as question marks, full stops, etc.

`label` is the piece of text preceding an input and is usually the question to be answered in the input.

##### Non-mandatory Attributes

There is also a non-mandatory attribute that can go with each field.

* `help_text` - Text that will appear under each field, usually an explanation or example answer to a question.

##### Field-specific Attributes
With several fields there are extra attributes required which are detailed below.

###### Groups / Sections
Sections and groups both require a `children` attribute, which is a list of fields are listed within.

Groups can also have a field called `isRepeatable` for when the whole group needs be be repeated on the questionaire
to allow repeated entries of the same type of certain data, such as a list of people's various details. An example group field is shown below.

```
{
    "type": "group", 
    "name": "authorised_persons", 
    "label": "Authorised Person",
    "isRepeatable": true, 
    "children": [
        {
            "type": "text", 
            "name": "ap_surname", 
            "label": "Surname"
        },
        {
            "type": "checkbox", 
            "name": "ap_given_names", 
            "label": "Given name(s)"
        }, 
        {
            "type": "date", 
            "name": "ap_dob", 
            "label": "Date of birth"
        } 
    ]
}
```

###### Select / Radiobuttons

These fields require an `options` attribute, which is the list of options for either the combo box or set of
radiobuttons. This is a list of objects with each object requiring a `value` and `label` attribute. `value` is the
actual value that will be stored in the database and `label` is the verbose version of the value. An optional field `defaultBlank` can be set to true if the initial chosen option in the combo box should be blank for `select` fields or no radiobuttons selected for `radiobuttons` fields. If `defaultBlank` is not set or false, the first option will be selected as default.

```
{
    "type": "select", 
    "name": "ap_association", 
    "label": "Association to applicant", 
    "defaultBlank": true
    "options": [
        {
            "value": "volunteer", 
            "label": "Volunteer"
        }, 
        {
            "value": "contractor", 
            "label": "Contractor"
        }, 
        {
            "value": "staff", 
            "label": "Staff / Employee"
        }, 
        {
            "value": "student", 
            "label": "Student"
        }, 
        {
            "value": "other", 
            "label": "Other - Please provide details"
        }
    ]
}
```

###### Checkboxes

Checkboxes differ slightly from other fields in that while they are often grouped together, they exist as separate
fields. In the case of checkbox fields, the label will appear next to the checkbox, rather than above, such that when
there is a sequence of checkbox fields they appear grouped together. As a result, a label field is usually required
before the sequence of checkbox fields, which will contain the question. This should not be confused with the label
attribute of a field - it is a field in its own right, and should have a label attribute within.

```
{
    "type": "label", 
    "name": "ap_handler_type", 
    "label": "Handler Type"
}, 
{
    "type": "checkbox", 
    "name": "ap_basic", 
    "label": "Basic handling, trap clearing and animal measurements"
}, 
{
    "type": "checkbox", 
    "name": "ap_biopsy", 
    "label": "Biopsy/tissue samples"
}, 
{
    "type": "checkbox", 
    "name": "ap_chipping", 
    "label": "Microchipping/tagging"
}
```

##### Conditions
There may be cases where a field or set of fields should only be shown if a particular answer is given for an earlier
field. To accomplish this, the `condition` attribute can be added to most field types, with the exception of
`section`, `group`, `label` and `file`. In practice, however, generally conditions would only be applied to
`select`, `radiobutton` and `checkbox` fields. A condition attribute should itself be a object, where each
attribute name is the answer that will yield further fields and the value of each attribute is the actual list of such
fields. Note: not all options require an entry in `conditions`, only the values that require further fields.

```
{
    "type": "radiobuttons", 
    "name": "how_project_funded", 
    "label": "How is your project funded?",
    "options": [
        {
            "value": "grant", 
            "label": "Grant / Sponsored"
        }, 
        {
            "value": "contract", 
            "label": "Contract / Consulting"
        }, 
        {
            "value": "other", 
            "label": "Other - Please provide details"
        }
    ], 
    "conditions": {
        "grant": [
            {
                "type": "text_area", 
                "name": "grant_details", 
                "label": "Provide details of the grant or sponsorship"
            }
        ],
        "contract": [
            {
                "type": "text", 
                "name": "contract_client_name", 
                "label": "Provide the client name."
            },
            {
                "type": "text_area", 
                "name": "contract_client_address", 
                "label": "Provide the client address."
            }
        ],
        "other": [
            {
                "type": "text_area", 
                "name": "financial_details_other", 
                "label": "Provide details of who is funding the project or how the project is being funded"
            }
        ]
    }
}
```

# API permissions

DRF endpoints require authentication by default through
`REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` in `disturbance/settings.py`.
Endpoint-specific permissions (for example internal-only classes) still apply on top of this.
An intentionally public DRF endpoint must declare `rest_framework.permissions.AllowAny`
explicitly and be added to `PUBLIC_DRF_VIEWS` in
`disturbance/tests/test_api_default_permissions.py`; never use an empty permission list.
This setting doesn't protect ordinary Django views, which need their own access controls.
