import gflags
import boto
import boto.ec2

FLAGS = gflags.FLAGS

gflags.DEFINE_string('hash', 'hash', 'The name of the tag key in which to store the instance hash value')

gflags.DEFINE_string('region', 'us-east-1', 'The EC2 region to connect to')
gflags.DEFINE_string('dryrun', False, 'Dryrun mode')

def main(argv=None, stdin=None, stdout=None, stderr=None):
    import sys
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                     (e, sys.argv[0], FLAGS))
        return 1
    
    tags = {}
    for k, v in (kv.split('=') for kv in argv):
        tags[k] = v
    if not tags:
        print "Cowardly refusing to run without any tags."
        print "I recommend you provide arguements like this: owner=prod app=waaa"
        exit(1)
    region = [r for r in boto.ec2.regions() if r.name == FLAGS.region][0]
    conn = region.connect()
    instances = []
    for instance in conn.get_only_instances():
        for k, v in tags.items():
            if instance.tags.get(k) != v:
                instance = None
                break
        if instance:
            instances.append(instance)
    
    missing = set()
    for instance in instances:
        if not instance.tags.get(FLAGS.hash):
            missing.add(instance)

    instances = [i for i in instances if i not in missing]
    missing = list(missing)
    existing_hashes = set(int(i.tags[FLAGS.hash] or 0) for i in instances)
    next = 1
    while missing:
        while next in existing_hashes:
            next += 1 
        if FLAGS.dryrun:
            print "Would add ", next, "to ", missing.pop()
        else:
            missing.pop().add_tag(FLAGS.hash, next)
        next += 1 
    
