
from sysdata.data_blob import dataBlob, source_dict
from syscore.objects import arg_not_supplied, get_class_name


source_dict['influx'] = "db"

class dataBlobWithInflux(dataBlob):

    def __init__(self, *args, **kwargs):
        super(dataBlobWithInflux, self).__init__(*args, **kwargs)

    def _add_influx_class(self, class_object):
        log = self._get_specific_logger(class_object)
        try:
            resolved_instance = class_object()
        except Exception as e:
            class_name = get_class_name(class_object)
            msg = (
                "Error %s couldn't evaluate %s(influx_db=self.influx_db, log = self.log.setup(component = %s)) \
                        This might be because import is missing\
                         or arguments don't follow pattern"
                % (str(e), class_name, class_name)
            )
            self._raise_and_log_error(msg)

        return resolved_instance

    def _get_class_adding_method(self, class_object):
        prefix = self._get_class_prefix(class_object)
        class_dict = dict(
            influx=self._add_influx_class,
        )

        method_to_add_with = class_dict.get(prefix, None)
        if method_to_add_with is None:
            method_to_add_with = super()._get_class_adding_method(class_object)

        return method_to_add_with