import consul

def service_registration(service_name, service_id, service_address, service_port, service_tags, service_interv):
    service = consul.Consul()
    check_inst = consul.Check.http(f'http://{service_address}:{service_port}/health', interval = service_interv)
    service.agent.service.register(name = service_name,
                                   service_id = service_id,
                                   address = service_address,
                                   port = int(service_port),
                                   tags = service_tags,
                                   check = check_inst)

def get_service_by_id(service_id):
    address_list = list()
    service = consul.Consul()
    index, services = service.health.service(service_id, passing = True)
    for service in services:
        socket = (service["Service"]["Address"], str(service["Service"]["Port"]))
        address_list.append(socket)
    
    return address_list

def get_kv(key):
    index = None
    service = consul.Consul()
    index, value = service.kv.get(key, index = index)
        
    return value
                     
def service_deregister(_id):
    service = consul.Consul()
    service.deregister(id=_id)

def service_list():
    service = consul.Consul()
    service.list()

def service_info(_name):
    service = consul.Consul()
    service.info(name=_name)