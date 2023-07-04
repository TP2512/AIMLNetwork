import logging
from vmwc import VMWareClient


class CommunicateToVMware:
    """
    This class is responsible to communicate to Vsphere server
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.vcenter_ip_address = kwargs.get('vcenter_ip')
        # self.vcenter_ip_address = kwargs.get('192.168.63.91')
        self.vcenter_user = kwargs.get('vcenter_user')
        self.vcenter_password = kwargs.get('vcenter_password')
        self.vcenter_operation = kwargs.get('operation')
        self.vcenter_vm_name = kwargs.get('vm_name')
        self.snapshot_name_create = kwargs.get('snapshot_name')
        self.snapshot_list = []
        self.vm = None

    def create_snapshot(self):

        """
        This function responsible to take a snapshot of current ACP version on Vsphere server
        """
        self.delete_snapshot()
        with VMWareClient(self.vcenter_ip_address, self.vcenter_user, self.vcenter_password) as client:
            for vm in client.get_virtual_machines():
                try:
                    if vm.name != self.vcenter_vm_name:
                        continue
                    vm.take_snapshot(self.snapshot_name_create, memory=False)
                    self.logger.info(f'Create snapshot "{self.snapshot_name_create}" is completed.')
                    return True
                except Exception:
                    self.logger.exception(f'Create snapshot failed for "{self.snapshot_name_create}"')
                    return False

    def delete_snapshot(self):
        """
        This function responsible to delete a snapshot from snapshot list on Vsphere server
        """
        with VMWareClient(self.vcenter_ip_address, self.vcenter_user, self.vcenter_password) as client:
            try:
                for vm in client.get_virtual_machines():
                    if vm.name == self.vcenter_vm_name:
                        self.vm = vm
                        self.logger.info(f'The VM name found successfully: {vm.name}')
                        for snapshot in vm.get_snapshots():
                            self.snapshot_list.append(snapshot)
                        self.logger.info(f'Snapshot List: {self.snapshot_list}')
                        break

                if len(self.snapshot_list) > 2:
                    for snap in self.snapshot_list:
                        snap.delete(remove_children=False)
                        self.snapshot_list.pop(0)
                        if len(self.snapshot_list) <= 2:
                            break
                        else:
                            continue
            except Exception:
                self.logger.exception('')
                return None
