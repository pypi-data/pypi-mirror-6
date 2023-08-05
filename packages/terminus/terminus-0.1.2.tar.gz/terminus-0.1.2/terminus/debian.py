import sys
from collections import OrderedDict
from terminus.util import is_comment


def is_ip_option(key, value):
    #ip_cmds = ['ip', 'route']
    ip_opts = ['address', 'gateway', 'network']
    action_opts = ['up', 'down', 'pre-up', 'pre-down']
    action_opt_route = ['ip', 'route']

    value_bits = value.split()
    has_ip = (key in ip_opts)
    is_action = (key in action_opts)
    #action_has_ip = (is_action and (value_bits[0] in ip_cmds))

    return has_ip \
        or (is_action and (value_bits[0] in action_opt_route or
                           value_bits[0:1] in action_opt_route))


class Interface(object):
    def __init__(self, name=None, driver=None, mode=None, auto=False):
        self.name = name
        self.driver = driver
        self.mode = []
        self.auto = auto
        self.hotplug = False
        self.config = OrderedDict()

        if mode:
            self.set_mode(mode)

    def __setitem__(self, key, value=None):
        self.config[key] = value

    def __getitem__(self, key):
        return self.config[key]

    def __delitem__(self, key):
        del self.config[key]

    def __repr__(self):
        return "<Interface %s, mode %s, driver %s, auto %s>" % (
            self.name, ' '.join(self.mode), self.driver, self.auto)

    def set_static(self):
        return self.set_mode('static')

    def set_manual(self):
        return self.set_mode('manual')

    def set_dhcp(self):
        return self.set_mode('dhcp')

    def set_mode(self, mode):
        self.mode = [mode]

    def set_hotplug(self, hotplug=True):
        self.hotplug = hotplug

    def is_bonded(self):
        return self.name[0:4] == 'bond'

    def options(self):
        for key, value in self.config.iteritems():
            yield key, value

    def ip_options(self):
        return [i for i in self.config.iteritems()
                if is_ip_option(i[0], i[1])]


class InterfacesFile(object):
    """
    So, this is terrible. To maintain ordering of the file, we have to jump
    through some serious hoops.

    TODO: Rewrite with objects instead, because readability and sanity will
    actually be a thing.

    """
    DefaultFile = '/etc/network/interfaces'

    def __init__(self, file_name=DefaultFile):
        self.interfaces = []
        self.raw = open(file_name).read()
        self.parse(self.raw)

    def parse(self, raw):
        iface = Interface()

        for line in raw.splitlines():
            bits = line.strip().split()
            if not line or not bits or is_comment(line):
                continue

            if bits[0] in ('auto', 'iface', 'allow-hotplug'):
                if iface.name and iface.name != bits[1]:
                    self.interfaces.append(iface)
                    iface = Interface()

            if 'auto' == bits[0]:
                iface.auto = True
            elif 'allow-hotplug' == bits[0]:
                iface.hotplug = True
            elif 'iface' == bits[0]:
                iface.name = bits[1]
                iface.driver = bits[2]
                iface.mode = bits[3:]
            elif iface:
                key = bits[0]
                value = ' '.join(bits[1:])
                iface[key] = value

        if iface and iface.name:
            self.interfaces.append(iface)

    def interface(self, name, proto='inet'):
        return filter(lambda intf: intf.name == name and intf.driver == proto,
                      self.interfaces)

    def has_bonded(self):
        for iface in self.interfaces:
            if iface.is_bonded():
                return True
        return False

    def move_ip_options(self, source_iface, target_iface):
        source = self.interface(source_iface)[0]
        target = self.interface(target_iface)[0]

        if not source or not target:
            return None

        source_opts = source.ip_options()
        for opt in source_opts:
            del(source[opt[0]])
            target[opt[0]] = opt[1]

        source.set_manual()

    def set_iface_mode(self, name, mode):
        for iface in self.interfaces:
            if iface.name == name:
                iface.set_mode(mode)
                return

    def add_iface(self, name=None, proto='inet', mode=None, auto=True):
        if self.interface(name, proto):
            raise Exception('An interface named %s with proto %s '
                            'already exists.' % (name, proto))

        iface = Interface(name=name, driver=proto, mode=mode, auto=auto)
        self.interfaces.append(iface)

    def write(self, target_file_name=sys.stdout):
        target = open(target_file_name, 'w')

        for iface in self.interfaces:
            if iface.auto:
                target.write('auto %s\n' % iface.name)

            if iface.hotplug:
                target.write('allow-hotplug %s\n' % iface.name)

            target.write('iface %s %s %s\n' % (iface.name, iface.driver,
                                               ' '.join(iface.mode)))

            for key, value in iface.options():
                target.write('    %s %s\n' % (key, value))

            target.write('\n')

        if target_file_name:
            target.close()
