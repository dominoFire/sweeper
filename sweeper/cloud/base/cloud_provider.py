

class CloudProvider:
    """
    A CloudProvider object represents a Cloud Computing service
    that sweeper can manage in order to execute a workflow in this
    cloud base
    """
    def __init__(self):
        """
        Default constructor. You should overwrite all of this
        class for creating a new Cloud base
        """
        self.name = "Base Cloud Provider"
        """Name of the cloud base"""

    def create_vm(self, name, config, **kwargs):
        """
        Creates a virtual machine in the cloud base service
        """
        raise NotImplementedError("You must implement create_vm")

    def delete_vm(self, name):
        """
        Deletes the named virtual machine provided by this CloudProvider

        :param name: Name of the cloud resource to delete from this cloud base
        :return: None
        """
        raise NotImplementedError("You must implement delete_vm")

    def get_config(self, config_name):
        """
        Get a configuration name provided

        :param config_name: Name of the Configuration Name provided by this cloud base
        :return: as ResourceConfig object
        """
        raise NotImplementedError("You must implement get_config")

    def list_configs(self):
        """
        List all available configurations provided by this cloud base

        :return: A list of ResourceConfig Objects
        """
        raise NotImplementedError("You must implement list_configs")

    # NOTE: We assume Method create_instance is implemented in each Cloud Provider Class
