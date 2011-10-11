#!/usr/local/bin/python
import sys, os, string
import urllib2

SVNLOOK='/usr/bin/svnlook'
TC_BUILD_STATUS_URL='http://<tc-server>:8111/guestAuth/app/rest/builds?locator=buildType:<build-type>,count:1'

def main(repos, txn):
    log_cmd = '%s log -t "%s" "%s"' % (SVNLOOK, txn, repos)
    log_msg = os.popen(log_cmd, 'r').readline().rstrip('\n')
    user_cmd = '%s author -t "%s" "%s"' % (SVNLOOK, txn, repos)
    user = os.popen(user_cmd, 'r').readline().rstrip('\n')

    if log_msg.find('#buildfix') > -1:
        sys.exit(0)
    if user == 'ciuser':
        sys.exit(0)

    if fetch_tc_status():
        sys.exit(0)
    else:
        sys.stderr.write ("Commits are forbidden because the build is broken. Add the tag #buildfix to the commit log to fix the build.\n")
        sys.exit(1)

def fetch_tc_status():
    req = urllib2.Request(TC_BUILD_STATUS_URL)
    req.add_header('Accept', 'application/json')
    try:
        response = urllib2.urlopen(req).read()
        status = eval(response)['build'][0]['status'] != 'FAILURE'
        return status
    except Exception, e:
        sys.stderr.write('Failed to get TC status: {0}\n'.format(e))
        return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s REPOS TXN\n" % (sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2])

