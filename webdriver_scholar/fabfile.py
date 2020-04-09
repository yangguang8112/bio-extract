from fabric.api import env, put

env.user = 'root'
env.hosts = ['209.250.236.46']
env.password = 'S,7aHvCm18tJ3thV'

# env.hosts = ['45.77.57.172']
# env.password = 'P@b26!jXCzJ.1?$a'


def d():
    put('../scholar', '~/')
