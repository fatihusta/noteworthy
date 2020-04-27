from django.db import models


class VPNDevice(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    wg_pubkey = models.CharField(max_length=44)
    wg_privkey = models.CharField(max_length=44)
    ipv4_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    ipv4_cidr_prefix = models.CharField(max_length=3, blank=True, null=True)
    ipv6_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    ipv6_cidr_prefix = models.CharField(max_length=3, blank=True, null=True)
    endpoint = models.GenericIPAddressField(protocol='IPv4')
    endpoint_port = models.IntegerField()
    allowed_ips = models.TextField()
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name
