import ConfigParser
import datetime
import json
import celery.loaders.base
import celery.schedules


class ZopeLoader(celery.loaders.base.BaseLoader):

    def __init__(self, app, **kwargs):
        self.celery_conf = kwargs.pop('celery_conf')
        self.zope_conf = kwargs.pop('zope_conf')

        super(ZopeLoader, self).__init__(app, **kwargs)

    def read_configuration(self, fail_silently=True):
        config = ConfigParser.SafeConfigParser()
        config.read(self.celery_conf)

        # Read main celery config
        config_dict = dict(
            [(key.upper(), value) for key, value in config.items('celery')])
        # Conversions
        config_dict['CELERY_IMPORTS'] = config_dict[
            'CELERY_IMPORTS'].split(',')
        # Explicitly tell celery to not hijack root logger since we
        # allow configuring our own own logger
        config_dict['CELERYD_HIJACK_ROOT_LOGGER'] = False

        # Read celery beat config
        beat_config = {}
        beat_sections = [
            c for c in config.sections() if c.startswith('celerybeat:')]
        for section in beat_sections:
            name = section.replace('celerybeat:', '', 1)

            schedule_type = config.get(section, 'type')
            schedule_value = json.loads(config.get(section, 'schedule'))
            if schedule_type == 'crontab':
                schedule = celery.schedules.crontab(**schedule_value)
            elif schedule_type == 'timedelta':
                schedule = datetime.timedelta(**schedule_value)
            elif schedule_type == 'integer':
                schedule = int(schedule_value)
            else:
                raise RuntimeError(
                    'No valid schedule type found in %s' % section)

            beat_config[name] = {
                'task': config.get(section, 'task'),
                'schedule': schedule}

        config_dict['CELERYBEAT_SCHEDULE'] = beat_config

        return config_dict

    def on_worker_process_init(self):
        """ Initialize the ZCA. """
        import zope.app.wsgi
        zope.app.wsgi.config(self.zope_conf)
