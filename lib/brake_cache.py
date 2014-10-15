from brake.backends import cachebe

# The default brake cache does not work with upstream load balancers.
class LoadBalancerCache(cachebe.CacheBackend):
    def get_ip(self, request):
        # Attempt to return x-forwarded-for if it exists, remote_addr otherwise.
        return request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))