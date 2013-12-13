from brake.backends import cachebe

# The default brake cache does not work with upstream load balancers.
class LoadBalancerCache(cachebe.CacheBackend):
    def get_ip(self, request):
        return request.META['X-FORWARDED-FOR']