import argparse
import json
import sys
import urllib2
import xml.etree.ElementTree as ElementTree


def main():
    parse_arguments(sys.argv[1:])
    op_keys = ['cmd_get', 'cmd_set', 'incr_misses', 'incr_hits', 'decr_misses',
               'decr_hits', 'delete_misses', 'delete_hits']
    average = dict()

    # Check if bucket is a list or not, sets it as first element if so
    if isinstance(args.bucket, list):
        args.bucket = args.bucket[0]
    endpoint = ('http://{}:8091/pools/default/buckets/{}/stats'
                .format(args.host_name[0], args.bucket))

    try:
        result = json.loads(urllib2.urlopen(endpoint).read())
    except urllib2.URLError:
        print ('Error accessing `{}`, please ensure that you have specified '
               'the correct bucket and hostname/IP'.format(endpoint))
        sys.exit(1)

    ops_dict = result['op']['samples']

    # Find 60 second average for each stat
    for op_key in op_keys:
        average[op_key] = sum(ops_dict[op_key]) / float(len(ops_dict[op_key]))

    average_ops_per_sec = sum(average.itervalues())

    # Generate the XML tree
    prtg = ElementTree.Element('prtg')
    xml_result = ElementTree.SubElement(prtg, 'result')
    channel = ElementTree.SubElement(xml_result, 'channel')
    channel.text = 'Couchbase Operations'
    value = ElementTree.SubElement(xml_result, 'value')
    value.text = str(average_ops_per_sec)
    xml_text = ElementTree.SubElement(prtg, 'text')
    xml_text.text = ('Average ops/s for past 60 seconds is {}'
                     .format(average_ops_per_sec))

    # Outputs the xml file based on the given parameters
    if args.output:
        with open(args.output[0], 'w') as f:
            f.write(ElementTree.tostring(prtg))
    else:
        print ElementTree.tostring(prtg)


def parse_arguments(arguments):
    # Parse the CLI arguments
    parser = argparse.ArgumentParser(description='Tool to find the average '
                                     'ops/s of a Couchbase Cluster and export '
                                     'that value into XML for PRTG reporting')
    parser.add_argument('host_name', nargs=1,
                        help='Host name/IP of the Couchbase cluster')
    parser.add_argument('--output', '-o', nargs=1,
                        help='Path of the output xml file')
    parser.add_argument('--bucket', '-b', nargs='*', default='default',
                        help='Name of bucket to gather stats for, defaults to '
                        'default bucket')
    global args
    args = parser.parse_args(arguments)

if __name__ == '__main__':
    main()
