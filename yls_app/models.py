from django.db import models

# Create your models here.
#class Family(models.Model):
#   serial_name = models.CharField(max_length=20,
#                                  help_text=_('Family of your product config'))
#   code_name = models.CharField(max_length=20,
#                                primary_key=True,
#                                validators = [RegexValidator(
#               r'[a-z].[a-z]*_*[a-z]*[0-9]*',
#               'only low case char and number and "_" is allowed',
#               'code name'
#           ),
#           MinLengthValidator(3),
#           MaxLengthValidator(20),
#       ])
#   is_alias_product = models.BooleanField(default=False)

#    TYPE_OPTION="TYPE_OPTION"
#   TYPE_UPLOAD="TYPE_UPLOAD"
#   TYPE_EDITBOX="TYPE_EDITBOX"
#   TYPE_CHECKBOX = "TYPE_CHECKBOX"
#   TYPE_OPTION_SKU_FAB="TYPE_OPTION_SKU_FAB"

#   INPUT_TYPES = (
#       (TYPE_OPTION, "Select feature via radio button"),
#       (TYPE_UPLOAD, "Upload a file"),
#       (TYPE_EDITBOX,"Input feature via text"),
#       (TYPE_CHECKBOX, "Check Box for a feature"),
#       (TYPE_OPTION_SKU_FAB,"Select feature via radiobuttons and two extra text field"),)

#   feature_type = models.CharField(max_length=20,
#                                   choices=FEATURES_TYPES,
#                                   help_text=_("Feature's type"))

#   feature_choices = models.ManyToManyField(SelectableFeatureChoices,
#                                             verbose_name="Choice to feature")

