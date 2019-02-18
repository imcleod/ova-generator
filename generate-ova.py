#!/usr/bin/python2

from imagefactory_plugins.ovfcommon.ovfcommon import VsphereOVFPackage
from imgfac.BaseImage import BaseImage
import tempfile
import os
import sys
import json
from subprocess import check_call
from stat import *
from shutil import rmtree, move

input_image = sys.argv[1]
image_parameters_file = sys.argv[2]
image_parameters = json.loads(open(image_parameters_file).read())
output_image = sys.argv[3]

vmdk_working_path = tempfile.mkdtemp(dir="/tmp")
os.chmod(vmdk_working_path, S_IRUSR|S_IWUSR|S_IXUSR|S_IRGRP|S_IXGRP|S_IROTH|S_IXOTH)

vmdk_image = os.path.join(vmdk_working_path, "image.vmdk")
print vmdk_image
check_call([ "qemu-img", "convert", "-f", "qcow2", "-O", "vmdk", "-o", 
             "adapter_type=lsilogic,subformat=streamOptimized,compat6",
             input_image, vmdk_image ])
print "Done with conversion"

ova_working_path = tempfile.mkdtemp(dir="/tmp")
os.chmod(ova_working_path, S_IRUSR|S_IWUSR|S_IXUSR|S_IRGRP|S_IXGRP|S_IROTH|S_IXOTH)

# The OVA code in factory uses the original qcow2 image to determine size
# We have access to that image so it is easy enough to just fake the existence
# of a BaseImage here
baseimage = BaseImage()
baseimage.data = input_image

pkg = VsphereOVFPackage(vmdk_image,baseimage, ova_working_path, **image_parameters)
ova = pkg.make_ova_package()
print ova
move(ova, output_image)
rmtree(vmdk_working_path)
rmtree(ova_working_path)


comments="""
           params = ['ovf_cpu_count','ovf_memory_mb','ovf_name',
                      'rhevm_default_display_type','rhevm_description','rhevm_os_descriptor',
                      'vsphere_product_name','vsphere_product_vendor_name','vsphere_product_version',
                      'vsphere_virtual_system_type', 'vsphere_scsi_controller_type',
                      'vsphere_network_controller_type', 'vsphere_nested_virt', 'vsphere_cdrom', 'vsphere_os_type',
                      'fusion_scsi_controller_type', 'fusion_network_controller_type', 'fusion_nested_virt',
                      'hyperv_vagrant',
                      'vagrant_sync_directory']

            for param in params:
                if (self.parameters.get(param) and
                    klass.__init__.func_code.co_varnames.__contains__(param)):
                    klass_parameters[param] = self.parameters.get(param)

        pkg = klass(disk=self.image.data, base_image=self.base_image,
                    **klass_parameters)
        ova = pkg.make_ova_package()
        copyfile_sparse(ova, self.image.data)
        pkg.delete()



class VsphereOVFPackage(OVFPackage):
    def __init__(self, disk, base_image, path=None,
                 ovf_cpu_count="2",
                 ovf_memory_mb="4096",
                 vsphere_product_name="Product Name",
                 vsphere_product_vendor_name="Vendor Name",
                 vsphere_product_version="1.0",
                 vsphere_virtual_system_type="vmx-07 vmx-08",
                 vsphere_nested_virt="false",
                 vsphere_os_type="rhel6_64Guest",
                 vsphere_cdrom="false",
                 vsphere_scsi_controller_type="lsilogic",
                 vsphere_network_controller_type="E1000"):

                 """

