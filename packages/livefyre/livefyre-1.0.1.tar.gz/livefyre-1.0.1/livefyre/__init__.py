from src.core import Network

class Livefyre(object):
    @staticmethod
    def get_network(network_name, network_key):
        return Network(network_name, network_key)