With this element other elements can register their installation source by
placing their details in the file source-repository-\*. An example
of an element "custom-element" that wants to retrieve the ironic source
from git and pbr from a tarball would be

*File : elements/custom-element/source-repository-ironic*

    #<name> <type> <destination> <location> [<ref>]
    # <ref> defaults to master if not specified
    ironic git /usr/local/ironic git://git.openstack.org/openstack/ironic.git

*File : elements/custom-element/source-repository-pbr*

    pbr tar /usr/local/pbr http://tarballs.openstack.org/pbr/pbr-master.tar.gz

diskimage-builder will then retrieve the sources specified and place them
at the directory \<destination\>

A number of environment variables can be set by the process calling
diskimage-builder which can change the details registered by the element, these are

    DIB_REPOTYPE_<name>     : change the registered type
    DIB_REPOLOCATION_<name> : change the registered location
    DIB_REPOREF_<name>      : change the registered reference

for example if you would like diskimage-builder to get ironic from a local
mirror you could set DIB_REPOLOCATION_ironic=git://localgitserver/ironic.git

Alternatively if you would like to use the keystone element and build an image with
keystone from a stable branch then you would set DIB_REPOREF_keystone=stable/grizzly

If you wish to build an image using code from a gerrit review, you can set 
DIB_REPOLOCATION_<name> and DIB_REPOREF_<name> to the values given by gerrit in the
fetch/pull section of a review. For example:

    DIB_REPOLOCATION_nova=https://review.openstack.org/openstack/nova
    DIB_REPOREF_nova=refs/changes/72/61972/8

Git sources will be cloned to \<destination\>

Tarballs will be extracted to \<destination\>. Tarballs should contain a
single topleval directory, regardless of the name of this top level directory
it will be renamed to \<destination\>

The package type indicates the element should install from packages onto the
root filesystem of the image build during the install.d phase.

If multiple elements register a source location with the same <destination>
then source-repositories will exit with an error. Care should therefore be taken
to only use elements together that download source to different locations.

The repository paths built into the image are stored in
etc/dib-source-repositories, one repository per line. This permits later review
of the repositories (by users or by other elements).

The repository names and types are written to an environment.d hook script at
01-source-repositories-environment. This allows later hook scripts during the
install.d phase to know which install type to use for the element.
