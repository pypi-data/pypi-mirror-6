from __future__ import print_function, division, absolute_import
import requests

from doto.logger import log
from doto.config import Config
from doto.droplet import Droplet
from doto.image import Image
from doto.domain import Domain
from doto.d0_mixin import d0mixin
from Crypto.PublicKey import RSA
import os
from os.path import join as pjoin

try:
  os.path.expanduser('~')
  expanduser = os.path.expanduser
except (AttributeError, ImportError):
  # This is probably running on App Engine.
  expanduser = (lambda x: x)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

BASEURL = "https://api.digitalocean.com"

class connect_d0(d0mixin):

    def __init__(self, path=None,debug=True):

        #logging is off when log.disabled is set to True
        if not debug:
            log.disabled = True

        self.config = Config(path)
        self._client_id = self.config.get('Credentials','client_id')
        self._api_key = self.config.get('Credentials','api_key')

    def __str__(self):
        return "DigitialOcean Connection Object"

    def __repr__(self):
        return "D0:Connected"

    def _set_logging(self,debug=True):
        """
        Convenience function to set logging on/off
        """

        #logging is off when log.disabled is set to True
        if not debug:
            log.disabled = True

        else:
            log.disabled = False


    def _attach_auth(self,items):
        """
        convenience method to attach client_id and api_key to
        Image or Droplet object
        """

        for d in items:
            #convert dictionary to droplet objects
            d['_client_id'] = self._client_id
            d['_api_key'] = self._api_key

        return items

    def _pprint_table(self, data):
        """
        pprint table: from stackoverflow:
        http://stackoverflow.com/a/8356620
        """

        table = []
        for d in data:
            table.append([unicode(v) for v in d.values()])

        header = d.keys()
        table.insert(0,header)

        col_width = [max(len(x) for x in col) for col in zip(*table)]
        for line in table:
            print("| " + " | ".join("{:{}}".format(x, col_width[i])
                                    for i, x in enumerate(line)) + " |")




    def create_droplet(self,name=None,size_id=None,image_id=None,
                       region_id=None,ssh_key_ids=None,private_networking=None):
        """
        Creates a droplet

        :type name: string
        :param name: The NAME of the droplet (name will be used as a reference
        on D0's servers)

        :type size_id: int
        :param size_id: The ID corresponding to requested size of the image (see
        connect_d0.get_sizes)

        :type image_id: int
        :param image_id: The ID corresponding to the requested image (see
        connect_d0.images)

        :type region_id: int
        :param region_id: The ID corresponding to the requested region (see
        connect_d0.region_id)

        :type ssh_key_ids: int
        :param ssh_key_ids: An optional list of comma separated IDs corresponding
        to the requested ssh_keys to be added to the server
        (see connect_d0.get_ssh_keys)

        :type private_networking: int
        :param private_networking: An optional bool which enables a private network interface
        if the region supports private networking

        droplet = d0.create_droplet(name='Random',
                               size_id=66, #512MB
                               image_id=1341147, #Docker 0.7 Ubuntu 13.04 x64
                               region_id=1, #New York
                               ssh_key_ids=18669
                               )
        """

        #ssh_key_ids check/convert to string
        if isinstance(ssh_key_ids,(tuple,list)):
            ssh_key_ids = ', '.join(str(key) for key in ssh_key_ids)

        data = self._request("/droplets/new",name=name,
                          size_id=size_id,image_id=image_id,
                          region_id=region_id,ssh_key_ids=ssh_key_ids,
                          private_networking=private_networking)

        #don't like this but will do for now
        data['droplet']['_client_id'] = self._client_id
        data['droplet']['_api_key'] = self._api_key
        droplet = Droplet(**data['droplet'])

        droplet.update()
        droplet.event_update()

        return droplet

        # https://api.digitalocean.com/droplets/new?client_id=[your_client_id]&api_key=[your_api_key]&
        # name=[droplet_name]&size_id=[size_id]&image_id=[image_id]&region_id=[region_id]&ssh_key_ids=
        # [ssh_key_id1],[ssh_key_id2]

    def get_droplet_by_name(self, name):
        """
        Convenience method to make it easy to select a droplet by name
        """
        droplets = self.get_all_droplets()
        for d in droplets:
            if d.name == name:
              return d
        return None


    def get_all_droplets(self,filters=None, status_check=None, table=False, raw_data=False):
        """
        This method returns all active droplets that are currently running in your account.
        All available API information is presented for each droplet.

        https://api.digitalocean.com/droplets/?
        client_id=[your_client_id]&api_key=[your_api_key]

        :rtype: list
        :return: A list of :class:`doto.Droplet`
        """


        log.info("Get All Droplets")
        data = self._request("/droplets",status_check)

        if status_check:
            return data

        if raw_data:
            return data

        if table:
            self._pprint_table(data['droplets'])
            return

        droplets = self._attach_auth(data['droplets'])

        if filters:
            droplets = [Droplet(**drop) for drop in droplets]
            for k,v in filters.iteritems():
                droplets = filter(lambda x: v in getattr(x,k), droplets)

            return droplets


        #convert dictionary to droplet objects
        return [Droplet(**drop) for drop in droplets]

    def get_droplet(self, id=None):
        """
        This method returns full information for a specific droplet ID that is passed in the URL.

        :type id: int
        :param id: ID of the droplet

        https://api.digitalocean.com/droplets/[droplet_id]?
        client_id=[your_client_id]&api_key=[your_api_key]

        """

        data = self._request("/droplets/"+str(id))

        #don't like this but will do for now
        data['droplet']['_client_id'] = self._client_id
        data['droplet']['_api_key'] = self._api_key

        #convert dictionary to droplet objects
        return Droplet(**data['droplet'])


    def get_sizes(self,status_check=None, table=False):
        """
        This method returns all the available sizes that can be used to create a droplet.


        https://api.digitalocean.com/sizes/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        data = self._request("/sizes", status_check)

        if status_check:
            return data

        sizes = data['sizes']
        if table:
            self._pprint_table(sizes)

        return sizes


    def get_all_regions(self,status_check=None, table=False):
        """
        This method will return all the available regions within the DigitalOcean cloud.

        https://api.digitalocean.com/sizes/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        data = self._request("/regions", status_check)

        if status_check:
            return data

        regions = data['regions']


        if table:
            self._pprint_table(regions)

        return  regions

    def get_domains(self, status_check=None, table=False):
        """
        This method returns all of your current domains.

        https://api.digitalocean.com/domains/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """


        data = self._request("/domains", status_check)
        if status_check:
            return data

        domains = data['domains']

        if table:
            self._pprint_table(domains)

        return domains

    def get_all_ssh_keys(self, status_check=None, table=False):
        """
        This method lists all the available public SSH keys in
        your account that can be added to a droplet.

        https://api.digitalocean.com/ssh_keys/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """


        data = self._request("/ssh_keys", status_check)

        if status_check:
            return data

        sshkeys = data['ssh_keys']

        if table:
            self._pprint_table(sshkeys)

        return sshkeys

    def create_key_pair(self, ssh_key_name=None, dry_run=False):
        """
        Method to create a key pair and store the public key on Digital Ocean's servers

        :type ssh_key_name: string
        :param ssh_key_name: The name of the new keypair

        :type dry_run: bool
        :param dry_run: Set to True if the operation should not actually run.

        :rtype: dict
        :return: Dictionary of SSH key info and local path

        https://api.digitalocean.com/ssh_keys/new/?name=[ssh_key_name]&ssh_pub_key=[ssh_public_key]&
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        ssh_path = pjoin(expanduser('~'), '.ssh')

        if not os.path.isdir(ssh_path): os.makedirs(ssh_path)

        #store key file in ~/.ssh
        keyfile = pjoin(ssh_path, ssh_key_name)

        key = RSA.generate(2048,os.urandom)

        #public key
        with open(keyfile+'_rsa.pub','w') as f:
            f.write(key.exportKey('OpenSSH'))
        public_key = key.exportKey('OpenSSH')
        os.chmod(keyfile+'_rsa.pub', 0o0600)

        #private key
        with open(keyfile+'_rsa','w') as f:
            f.write(key.exportKey())

        os.chmod(keyfile+'_rsa', 0o0600)

        data = self._request("/ssh_keys/new/", name=ssh_key_name,
                             ssh_pub_key=public_key)

        #include path to newly created file
        data['ssh_key']['path'] = keyfile+'_rsa'

        log.info(data['ssh_key'])
        return data['ssh_key']

    def delete_key_pair(self, ssh_key_id=None):
        """
        Delete the SSH key from your account.

        :type ssh_key_id: int
        :param ssh_key_id: The ID of the public key

        https://api.digitalocean.com/ssh_keys/[ssh_key_id]/destroy/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        url = "/ssh_keys/%d/destroy" % (ssh_key_id)

        data = self._request(url)

        log.info(data)

    def get_ssh_key(self, ssh_key_id=None):
        """
        Delete the SSH key from your account.

        :type ssh_key_id: int
        :param ssh_key_id: The ID of the public key

        https://api.digitalocean.com/ssh_keys/[ssh_key_id]/destroy/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        url = "/ssh_keys/%d" % (ssh_key_id)

        data = self._request(url)

        log.info(data)

    def get_all_images(self, filters=None, status_check=False, table=False, raw_data=False):
        """
        Convenience method to get Digital Ocean's list of public images
        and users current private images
        using EC2 style filtering

        https://api.digitalocean.com/sizes/?client_id=[your_client_id]&api_key=[your_api_key]

        :type filters: dict
        :param filters: Optional filters that can be used to limit the
            results returned.  Filters are provided in the form of a
            dictionary consisting of filter names as the key and
            filter values as the value.  The set of allowable filter
            names/values is dependent on the request being performed.
            Check the DigitalOcean API guide for details.

        :rtype: list
        :return: A list of :class:`doto.Image` objects


        https://api.digitalocean.com/images/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        data = self._request("/images", status_check)

        if raw_data:
            return data

        if status_check:
            return data

        if table:
            self._pprint_table(data['images'])
            return

        images = self._attach_auth(data['images'])


        if filters:
            images = [Image(**img) for img in images]
            for k,v in filters.iteritems():
                images = filter(lambda x: v in getattr(x,k), images)

            return images

        #convert dictionary to Image objects
        return [Image(**img) for img in images]


    def get_image(self, image_id=None):
        """
        This method displays the attributes of an image.

        :type image_id: int
        :param image_id: The ID of the image

        :rtype: :class:`doto.Image`
        :return: The newly created :class:`doto.Image`.

        https://api.digitalocean.com/images/[image_id]/?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        url = "/images/%d" % (image_id)

        data = self._request(url)


        log.info(data)

        #don't like this but will do for now
        data['image']['_client_id'] = self._client_id
        data['image']['_api_key'] = self._api_key


        return Image(**data['image'])

    def get_all_domains(self,filters=None, status_check=None, table=False, raw_data=False):
        """
        This method returns all active droplets that are currently running in your account.
        All available API information is presented for each droplet.

        https://api.digitalocean.com/droplets/?
        client_id=[your_client_id]&api_key=[your_api_key]

        :rtype: list
        :return: A list of :class:`doto.Droplet`
        """

        data = self._request("/domains",status_check)

        if status_check:
            return data

        if raw_data:
            return data

        if table:
            self._pprint_table(data['domains'])
            return

        domains = self._attach_auth(data['domains'])

        if filters:
            droplets = [Droplet(**drop) for drop in domains]
            for k,v in filters.iteritems():
                droplets = filter(lambda x: v in getattr(x,k), droplets)

            return droplets


        #convert dictionary to droplet objects
        return [Domain(**dom) for dom in domains]

    def create_domain(self,name=None,ip_addr=None):
        """
        This method creates a new domain name with an A record for the specified [ip_address].

        :type name: string
        :param size: The NAME of the domain


        :type ip_address: string
        :param size: ip address for the domain's initial a record.

        https://api.digitalocean.com/domains/new?
        client_id=[your_client_id]&api_key=[your_api_key]&name=[domain]&ip_address=[ip_address]
        """


        log.info("Creating new domain")

        data = self._request("/domains/new",name=name,
                          ip_address=ip_addr)

        log.debug(data)

        #don't like this but will do for now
        data['domain']['_client_id'] = self._client_id
        data['domain']['_api_key'] = self._api_key
        domain = Domain(**data['domain'])

        return domain

    def get_domain(self, domain_id=None):
        """
        This method displays the attributes of an image.

        :type image_id: int
        :param image_id: The ID of the image

        :rtype: :class:`doto.Image`
        :return: The newly created :class:`doto.Image`.

        https://api.digitalocean.com/domains/[domain_id]?
        client_id=[your_client_id]&api_key=[your_api_key]
        """

        url = "/domains/%d" % (domain_id)

        data = self._request(url)


        log.debug(data)

        #don't like this but will do for now
        data['domain']['_client_id'] = self._client_id
        data['domain']['_api_key'] = self._api_key


        return Domain(**data['domain'])

