import logging
from vedavaapi.common import VedavaapiServices

def register_service(app, svcname, reset=False):
    svc_cls = "Vedavaapi" + str.capitalize(svcname)
    _tmp = __import__('vedavaapi.{}'.format(svcname), globals(), locals(), [svc_cls])
    svc_cls = eval('_tmp.' + svc_cls)

    try:
        '''starts dependency services. thus no problem with order of initiation.'''
        for dep in svc_cls.dependency_services:
            VedavaapiServices.start(dep, reset)
    except Exception as e:
        pass

    svc_conf = VedavaapiServices.server_config[svcname] if svcname in VedavaapiServices.server_config else {}
    svc_obj = svc_cls(VedavaapiServices, svcname, svc_conf)
    VedavaapiServices.register(svcname, svc_obj)

    if reset:
        logging.info("Resetting previous state of {} ...".format(svcname))
        svc_obj.reset()
        VedavaapiServices.lookup("store")
    svc_obj.setup()
    svc_obj.register_api(app, "/{}".format(svcname))


def setup_services(app, config_file, services, reset=False):
    if not services:
        return

    VedavaapiServices.set_config(config_file_name=config_file)

    for svc in services:
        register_service(app, svc, reset)

