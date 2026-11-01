"""Read AWS state and prepare exact digest-pinned requests; does not provision resources."""
import argparse
import datetime as dt
import ipaddress
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['service', 'expiry'])
    parser.add_argument('--directory', type=Path, default=Path('runtime/aws-deploy-20261102'))
    parser.add_argument('--profile', default='reflex-aws')
    parser.add_argument('--region', default='ap-southeast-2')
    args = parser.parse_args()
    if args.directory.resolve().is_relative_to(Path('infra').resolve()):
        parser.error('Account-specific requests belong in ignored runtime storage.')
    args.directory.mkdir(parents=True, exist_ok=True)

    def aws(*command):
        result = subprocess.run(['aws', *command, '--profile', args.profile, '--region', args.region,
                                 '--output', 'json', '--no-cli-pager'], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def stack(name):
        item = aws('cloudformation', 'describe-stacks', '--stack-name', name)['Stacks'][0]
        if item['StackStatus'] not in {'CREATE_COMPLETE', 'UPDATE_COMPLETE'}:
            raise RuntimeError(f'{name} is not ready: {item["StackStatus"]}')
        return item, {r['OutputKey']: r['OutputValue'] for r in item.get('Outputs', [])}

    def save(name, value):
        (args.directory / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

    foundation, outputs = stack('steplock-foundation')
    plan = json.loads((args.directory / 'plan.json').read_text())
    if args.stage == 'service':
        image = aws('ecr', 'describe-images', '--repository-name', outputs['ImageRepositoryName'],
                    '--image-ids', 'imageTag=' + plan['source_commit'])['imageDetails'][0]
        digest = image['imageDigest']
        if not digest.startswith('sha256:') or len(digest) != 71:
            raise RuntimeError('Image digest is invalid')
        with urlopen('https://checkip.amazonaws.com', timeout=10) as response:
            address = ipaddress.ip_address(response.read().decode().strip())
        if address.version != 4:
            raise RuntimeError('Staging currently requires an IPv4 test address')
        params = {k: outputs[k] for k in ['ClusterArn', 'SubnetA', 'SubnetB', 'ExecutionRoleArn',
                                         'InfrastructureRoleArn', 'LogGroupName']}
        params.update(ImageUri=outputs['ImageRepositoryUri'] + '@' + digest,
                      TestIpv4=str(address) + '/32', Access='restricted', TrustedHosts='127.0.0.1,localhost')
        save('image.json', {'source_commit': plan['source_commit'], 'image_digest': digest,
                            'image_size_bytes': image['imageSizeInBytes']})
        save('service-parameters.json', [{'ParameterKey': k, 'ParameterValue': v} for k, v in params.items()])
        print(json.dumps({'parameters_prepared': True, 'digest': digest, 'access': 'restricted'}))
        return

    service, service_outputs = stack('steplock-service')
    probe, _ = stack('steplock-expiry-probe')
    account = aws('sts', 'get-caller-identity')['Account']
    prefix = f'arn:aws:'
    resources, roles = set(), set()
    mapping = {'AWS::EC2::VPC': 'vpc', 'AWS::EC2::Subnet': 'subnet',
               'AWS::EC2::InternetGateway': 'internet-gateway', 'AWS::EC2::RouteTable': 'route-table'}
    rows = aws('cloudformation', 'list-stack-resources', '--stack-name', 'steplock-foundation')['StackResourceSummaries']
    for row in rows:
        kind, physical = row['ResourceType'], row['PhysicalResourceId']
        if kind in mapping:
            resources.add(f'{prefix}ec2:{args.region}:{account}:{mapping[kind]}/{physical}')
        elif kind == 'AWS::IAM::Role':
            roles.add(f'{prefix}iam::{account}:role/{physical}')
        elif kind == 'AWS::Logs::LogGroup':
            resources.update([f'{prefix}logs:{args.region}:{account}:log-group:{physical}',
                              f'{prefix}logs:{args.region}:{account}:log-group:{physical}:*'])
        elif kind == 'AWS::ECR::Repository':
            resources.add(f'{prefix}ecr:{args.region}:{account}:repository/{physical}')
        elif kind == 'AWS::CodeBuild::Project':
            resources.add(f'{prefix}codebuild:{args.region}:{account}:project/{physical}')
        elif kind == 'AWS::ECS::Cluster':
            resources.add(outputs['ClusterArn'])
    resources.update(roles)
    for key in ['ServiceArn', 'LoadBalancerArn', 'WebAclArn', 'TestIpsArn']:
        resources.add(service_outputs[key])
    probe_log = '/aws/steplock/steplock-expiry-probe'
    resources.update([f'{prefix}logs:{args.region}:{account}:log-group:{probe_log}',
                      f'{prefix}logs:{args.region}:{account}:log-group:{probe_log}:*'])
    if any('reflex' in arn.lower() or f':{account}:' not in arn for arn in resources):
        raise RuntimeError('Foreign resource in teardown inventory')
    params = {'ServiceStackArn': service['StackId'], 'FoundationStackArn': foundation['StackId'],
              'ProbeStackArn': probe['StackId'], 'DeletionResourceArns': ','.join(sorted(resources)),
              'TrialRoleArns': ','.join(sorted(roles)), 'TeardownAt': plan['service_teardown_utc'],
              'FoundationTeardownAt': plan['foundation_teardown_utc'],
              'ProbeAt': (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=4)).strftime('%Y-%m-%dT%H:%M:%S')}
    save('expiry-parameters.json', [{'ParameterKey': k, 'ParameterValue': v} for k, v in params.items()])
    save('teardown-inventory.json', {'stack_arns': [service['StackId'], foundation['StackId'], probe['StackId']],
                                     'resource_arns': sorted(resources), 'trial_role_arns': sorted(roles)})
    print(json.dumps({'parameters_prepared': True, 'resource_count': len(resources),
                      'service_teardown_utc': plan['service_teardown_utc'], 'probe_at': params['ProbeAt']}))


if __name__ == '__main__':
    main()
