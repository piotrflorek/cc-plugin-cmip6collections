"""
compliance_checker.cmip6collections

Compliance Test Suite for the CMIP6 project
"""

from compliance_checker.base import BaseCheck, BaseNCCheck, Result, TestCtx

# Import library to interact with Controlled Vocabularies
import pyessv
import os
from utils import StructuredDataset
from netCDF4 import Dataset

EPOCH = 'cmip6'
DRS_CANONICAL = 'canonical'

def validate_daterange(frequency):
    if frequency == "yr" or frequency == "decadal":
        template = "yyyy"
    elif frequency = "mon" or frequency == "monClim":
        template = "yyyyMM"


class BaseCMIP6Check(BaseCheck):
    @classmethod
    def make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    @classmethod
    def configure(cls, drs_convention, validate_directories, *args, **kwargs):
        cls.drs_convention = drs_convention
        cls.validate_directories = validate_directories

    def setup(self, ds):
        self._cache_controlled_vocabularies()
        self._cache_member_id_template()

    def _cache_controlled_vocabularies(self):
        """
        Loads controlled vocabularies once and caches them.
        """
        self._wcrp_cmip6_cv = pyessv.load('wcrp', EPOCH)
        self._authority = pyessv.load('wcrp')
        self._scope = pyessv.load('wcrp:cmip6')

    def _cache_member_id_template(self):
        self._member_id_regex = pyessv.create_collection(
            self._scope,
            'member-id',
            description='test',
            term_name_regex=r'^r\d+i\d+p\d+f\d+$'
        )


class CMIP6Check(BaseNCCheck, BaseCMIP6Check):
    register_checker = True
    name = 'cmip6'

    def check_filename(self, ds):
        """
        <variable_id>   tas
        <table_id>      Amon
        <source_id>     hadgem3-es
        <experiment_id> piCtrl
        <member_id>     r1i1p1f1
        <grid_label>    gn
        [<time_range>]  201601-210012
        .nc
        """
        template = '{}_{}_{}_{}.nc'

        collections = (
            self._wcrp_cmip6_cv['activity-id'],
            self._wcrp_cmip6_cv['institution-id'],
            self._wcrp_cmip6_cv['source-id'],
            self._wcrp_cmip6_cv['experiment-id'],
            self._member_id_regex,
        )

        parser = pyessv.create_template_parser(template, collections)

        level = BaseCheck.MEDIUM
        out_of = 0
        score = 0
        messages = []
        try:
            parser.parse(os.path.basename(ds.filepath()))
            score += 1
            out_of += 1
        except pyessv.TemplateParsingError:
            messages.append("{} is not a valid DRS structure".format(ds))

        return self.make_result(level, score, out_of, 'DRS structure', messages)

    def check_global_attributes(self, ds):
        # compare metadata
        attributes = ['activity-id', 'institution-id']
        for attr in attributes:
            nc_attr = ncfile.getncattr(attr.replace('-', '_'))
            allowed_values = [trm.label for trm in self._wcrp_cmip6_cv[attr].terms]
            if nc_attr not in allowed_values:
                messages.append("Attribute {} missing in the ncdf file {}".format(attr, nc_path))
        except Exception:
            print "woops"


class DRSCheck(BaseCMIP6Check):
    register_checker = True
    name = 'cmip6collections'

    drs_convention = 'canonical'
    validate_directories = True
    supported_ds = [StructuredDataset] #

    def check_drs_directories(self, ds):
        """
        Verifies the directory structure (order and vocabulary)
        /mip_era/
         activity_id/
          institution_id/
           source_id/
            experiment_id/
             member_id/
              table_id/
               variable_id/
                grid_label/
                 version
        """
        if not self.validate_directories:
            return None

        template = EPOCH + '/{}/{}/{}/{}/{}'

        collections = (
            self._wcrp_cmip6_cv['activity-id'],
            self._wcrp_cmip6_cv['institution-id'],
            self._wcrp_cmip6_cv['source-id'],
            self._wcrp_cmip6_cv['experiment-id'],
            self._member_id_regex
        )

        parser = pyessv.create_template_parser(template, collections)

        level = BaseCheck.MEDIUM
        out_of = 0
        score = 0
        messages = []
        for nc_path in ds.get_filepaths():
            out_of += 1
            subpath = os.path.dirname(nc_path).replace(ds.get_root(), '')
            ncfile = Dataset(nc_path)

            try:
                parsed = parser.parse(subpath)
                for collection_name in parsed:
                    if collection_name == 'member-id':
                        attr_name = 'variant_id'  # TODO: implement subexperiments
                    else:
                        attr_name = collection_name.replace('-','_')

                    try:
                        nc_attr = ncfile.getncattr(attr_name)
                    except AttributeError as e:
                        messages.append("Attribute {} not found in the netcdf file".format(attr_name))
                    if nc_attr != parsed[collection_name]:
                        messages.append(
                            "DRS inconsistent with ncdf contents: {} != {} ({})"
                            .format(nc_attr, parsed[collection_name], attr_name)
                        )
                score += 1
            except pyessv.TemplateParsingError as e:
                messages.append("{} is not a valid DRS hierarchy ({})".format(subpath, e.message))
       return self.make_result(level, score, out_of, 'DRS structure', messages)
