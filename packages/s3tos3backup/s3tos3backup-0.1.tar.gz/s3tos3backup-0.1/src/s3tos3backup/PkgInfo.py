try:
    distribution = __import__('pkg_resources') \
        .get_distribution('s3tos3backup')
    version = distribution.version
except Exception, e:
    version = 'unknown'

url = "https://github.com/YD-Technology/s3tos3backup"
