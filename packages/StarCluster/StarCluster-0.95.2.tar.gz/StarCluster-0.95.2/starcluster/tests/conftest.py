import pytest

from starcluster import static
from starcluster import config as sconfig
from starcluster import cluster as scluster

VPC_CIDR = '10.0.0.0/16'
SUBNET_CIDR = '10.0.0.0/24'


def pytest_addoption(parser):
    parser.addoption("-L", "--live", action="store_true", default=False,
                     help="Run live StarCluster tests on a real AWS account")
    parser.addoption("-C", "--coverage", action="store_true", default=False,
                     help="Produce a coverage report for StarCluster")


def pytest_runtest_setup(item):
    if 'live' in item.keywords and not item.config.getoption("--live"):
        pytest.skip("pass --live option to run")


def pytest_configure(config):
    if config.getoption("--coverage"):
        config.option.cov_source = ['starcluster']
        config.option.cov_report = ['term-missing']


@pytest.fixture(scope="module")
def keypair(ec2, config):
    keypairs = ec2.get_keypairs()
    for key in keypairs:
        if key.name in config.keys:
            key.key_location = config.keys[key.name].key_location
            return key
    raise Exception("no keypair on ec2 defined in config")


@pytest.fixture(scope="module")
def config():
    cfg = sconfig.StarClusterConfig().load()
    assert cfg.aws.aws_access_key_id
    assert cfg.aws.aws_secret_access_key
    return cfg


@pytest.fixture(scope="module")
def ec2(config):
    return config.get_easy_ec2()


@pytest.fixture(scope="module")
def vpc(ec2):
    vpcs = ec2.conn.get_all_vpcs(filters={'tag:test': True})
    if not vpcs:
        vpc = ec2.conn.create_vpc(VPC_CIDR)
        vpc.add_tag('test', True)
    else:
        vpc = vpcs.pop()
    return vpc


@pytest.fixture(scope="module")
def subnet(ec2, vpc):
    subnets = ec2.conn.get_all_subnets(
        filters={'vpcId': vpc.id, 'cidrBlock': SUBNET_CIDR})
    if not subnets:
        subnet = ec2.conn.create_subnet(vpc.id, SUBNET_CIDR)
    else:
        subnet = subnets.pop()
    return subnet


@pytest.fixture(scope="module")
def ami(ec2):
    img = ec2.conn.get_all_images(
        filters={'owner_id': static.STARCLUSTER_OWNER_ID,
                 'name': 'starcluster-base-ubuntu-13.04-x86_64'})
    assert len(img) == 1
    return img[0]


@pytest.fixture(scope="module",
                params=['flat', 'spot', 'vpc-flat', 'vpc-spot'])
def cluster(request, ec2, keypair, subnet, ami):
    size = 2
    shell = 'bash'
    user = 'testuser'
    subnet_id = subnet.id if 'vpc' in request.param else None
    spot_bid = 0.08 if 'spot' in request.param else None
    instance_type = 't1.micro'
    cl = scluster.Cluster(ec2_conn=ec2,
                          cluster_tag=request.param,
                          cluster_size=size,
                          cluster_user=user,
                          keyname=keypair.name,
                          key_location=keypair.key_location,
                          cluster_shell=shell,
                          master_instance_type=instance_type,
                          master_image_id=ami.id,
                          node_instance_type=instance_type,
                          node_image_id=ami,
                          spot_bid=spot_bid,
                          subnet_id=subnet_id)
    cl.start()
    assert cl.master_node
    assert len(cl.nodes) == size

    def terminate():
        try:
            cl.terminate_cluster()
        except:
            cl.terminate_cluster(force=True)
    request.addfinalizer(terminate)
    return cl


@pytest.fixture(scope="module")
def nodes(cluster):
    return cluster.nodes
