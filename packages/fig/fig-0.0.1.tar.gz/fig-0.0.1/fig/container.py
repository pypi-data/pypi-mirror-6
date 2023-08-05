import logging

log = logging.getLogger(__name__)

class Container(object):
    """
    Represents a Docker container, constructed from the output of 
    GET /containers/:id:/json.
    """
    def __init__(self, client, dictionary, has_been_inspected=False):
        self.client = client
        self.dictionary = dictionary
        self.has_been_inspected = has_been_inspected

    @classmethod
    def from_ps(cls, client, dictionary, **kwargs):
        """
        Construct a container object from the output of GET /containers/json.
        """
        new_dictionary = {
            'ID': dictionary['Id'],
            'Image': dictionary['Image'],
        }
        for name in dictionary.get('Names', []):
            if len(name.split('/')) == 2:
                new_dictionary['Name'] = name
        return cls(client, new_dictionary, **kwargs)

    @classmethod
    def from_id(cls, client, id):
        return cls(client, client.inspect_container(id))

    @classmethod
    def create(cls, client, **options):
        response = client.create_container(**options)
        return cls.from_id(client, response['Id'])

    @property
    def id(self):
        return self.dictionary['ID']

    @property
    def short_id(self):
        return self.id[:10]

    @property
    def name(self):
        return self.dictionary['Name'][1:]

    @property
    def human_readable_ports(self):
        self.inspect_if_not_inspected()
        if not self.dictionary['NetworkSettings']['Ports']:
            return ''
        ports = []
        for private, public in self.dictionary['NetworkSettings']['Ports'].items():
            if public:
                ports.append('%s->%s' % (public[0]['HostPort'], private))
        return ', '.join(ports)

    @property
    def human_readable_state(self):
        self.inspect_if_not_inspected()
        if self.dictionary['State']['Running']:
            if self.dictionary['State']['Ghost']:
                return 'Ghost'
            else:
                return 'Up'
        else:
            return 'Exit %s' % self.dictionary['State']['ExitCode']

    @property
    def human_readable_command(self):
        self.inspect_if_not_inspected()
        return ' '.join(self.dictionary['Config']['Cmd'])

    @property
    def environment(self):
        self.inspect_if_not_inspected()
        out = {}
        for var in self.dictionary.get('Config', {}).get('Env', []):
            k, v = var.split('=', 1)
            out[k] = v
        return out

    @property
    def is_running(self):
        self.inspect_if_not_inspected()
        return self.dictionary['State']['Running']

    def start(self, **options):
        log.info("Starting %s..." % self.name)
        return self.client.start(self.id, **options)

    def stop(self, **options):
        log.info("Stopping %s..." % self.name)
        return self.client.stop(self.id, **options)

    def kill(self):
        log.info("Killing %s..." % self.name)
        return self.client.kill(self.id)

    def remove(self):
        log.info("Removing %s..." % self.name)
        return self.client.remove_container(self.id)

    def inspect_if_not_inspected(self):
        if not self.has_been_inspected:
            self.inspect()

    def wait(self):
        return self.client.wait(self.id)

    def logs(self, *args, **kwargs):
        return self.client.logs(self.id, *args, **kwargs)

    def inspect(self):
        self.dictionary = self.client.inspect_container(self.id)
        return self.dictionary

    def links(self):
        links = []
        for container in self.client.containers():
            for name in container['Names']:
                bits = name.split('/')
                if len(bits) > 2 and bits[1] == self.name:
                    links.append(bits[2])
        return links

    def attach_socket(self, **kwargs):
        return self.client.attach_socket(self.id, **kwargs)

    def __repr__(self):
        return '<Container: %s>' % self.name

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.id == other.id
