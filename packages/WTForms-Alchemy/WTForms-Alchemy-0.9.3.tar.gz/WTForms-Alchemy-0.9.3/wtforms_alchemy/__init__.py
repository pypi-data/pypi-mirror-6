#import pytz
import six
from wtforms import Form
from wtforms.validators import InputRequired, DataRequired
from wtforms.form import FormMeta
from wtforms_components import (
    DateRange,
    NumberRangeField,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
)
from .utils import (
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)
from .exc import (
    AttributeTypeException,
    InvalidAttributeException,
    UnknownTypeException
)
from .fields import ModelFieldList, ModelFormField
from .generator import FormGenerator


__all__ = (
    AttributeTypeException,
    DateRange,
    InvalidAttributeException,
    ModelFieldList,
    ModelFormField,
    NumberRangeField,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
    UnknownTypeException,
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


__version__ = '0.9.3'


class ModelFormMeta(FormMeta):
    """Meta class that overrides WTForms base meta class. The primary purpose
    of this class is allowing ModelForms use special configuration params under
    the 'Meta' class namespace.

    ModelForm classes inherit parent's Meta class properties.
    """
    def __init__(cls, *args, **kwargs):
        bases = []
        for class_ in cls.__mro__:
            if 'Meta' in class_.__dict__:
                bases.append(getattr(class_, 'Meta'))

        cls.Meta = type('Meta', tuple(bases), {})

        FormMeta.__init__(cls, *args, **kwargs)

        if hasattr(cls.Meta, 'model') and cls.Meta.model:
            generator = cls.Meta.form_generator(cls)
            generator.create_form(cls)


def model_form_factory(base=Form, meta=ModelFormMeta, **defaults):
    """Creates new model form, with given base class."""

    class ModelForm(six.with_metaclass(meta, base)):
        """
        A function that returns SQLAlchemy session. This should be
        assigned if you wish to use Unique validator. If you are using
        Flask-SQLAlchemy along with WTForms-Alchemy you don't need to
        set this.
        """
        get_session = None

        class Meta:
            model = None

            default = None

            #: Whether or not to skip unknown types. If this is set to True,
            #: fields with types that are not present in FormGenerator type map
            #: will be silently excluded from the generated form.
            #:
            #: By default this is set to False, meaning unknown types throw
            #: exceptions when encountered.
            skip_unknown_types = defaults.get('skip_unknown_types', False)

            #: Whether or not to assign non-nullable fields as required
            assign_required = defaults.get('assign_required', True)

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = defaults.get('all_fields_optional', False)

            validators = {}

            #: A dict with keys as field names and values as field arguments.
            field_args = {}

            #: A dict with keys as field names and values as widget options.
            widget_options = {}

            #: Whether or not to include only indexed fields.
            only_indexed_fields = defaults.get('only_indexed_fields', False)

            #: Whether or not to include primary keys.
            include_primary_keys = defaults.get('include_primary_keys', False)

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = defaults.get('include_foreign_keys', False)

            #: Whether or not to strip string fields
            strip_string_fields = defaults.get('strip_string_fields', False)

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = defaults.get(
                'include_datetimes_with_default', False
            )

            #: The default validator to be used for not nullable columns. Set
            #: this to `None` if you wish to disable it.
            not_null_validator = InputRequired()

            #: The default validator to be used for not nullable string
            #: columns. If this is set to `None` the configuration option
            #: `not_null_validator` will be used for string columns also.
            not_null_str_validator = [InputRequired(), DataRequired()]

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
            form_generator = defaults.get(
                'form_generator', FormGenerator
            )

            #: Default date format
            date_format = defaults.get('date_format', '%Y-%m-%d')

            #: Default datetime format
            datetime_format = defaults.get(
                'datetime_format', '%Y-%m-%d %H:%M:%S'
            )

            #: Dictionary of SQLAlchemy types as keys and WTForms field classes
            #: as values. The key value pairs of this dictionary override
            #: the key value pairs of FormGenerator.TYPE_MAP.
            #:
            #: Using this configuration option one can easily configure the
            #: type conversion in class level.
            type_map = {}

            #: Additional fields to include in the generated form.
            include = []

            #: List of fields to exclude from the generated form.
            exclude = []

            #: List of fields to only include in the generated form.
            only = []

        def __init__(self, *args, **kwargs):
            """Sets object as form attribute."""

            self._obj = kwargs.get('obj', None)
            super(ModelForm, self).__init__(*args, **kwargs)

    return ModelForm


ModelForm = model_form_factory(Form)


class ModelCreateForm(ModelForm):
    pass


class ModelUpdateForm(ModelForm):
    class Meta:
        all_fields_optional = True
        assign_required = False


class ModelSearchForm(ModelForm):
    class Meta:
        all_fields_optional = True
        only_indexed_fields = True
        include_primary_keys = True
