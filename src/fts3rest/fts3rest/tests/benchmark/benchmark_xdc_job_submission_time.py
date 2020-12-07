import os
from datetime import datetime, timedelta
from optparse import OptionParser
from util import  *


script_transfer_path = '/home/aris/projects/fts-rest/src/cli/fts-rest-transfer-submit'
script_whoami_path = '/home/aris/projects/fts-rest/src/cli/fts-rest-whoami'


def benchmark_transfer_auth(opts, auth_method='OAuth2'):
    log.info("Starting benchmark for auth method {0} with {1} files".format(auth_method, str(opts.files_number)))

    duration = timedelta()
    for f in xrange(opts.files_number):
        src = "gsiftp://source.se/path/file..%d" % f
        dst = "gsiftp://dest.se/path/file.%d" % f
        if auth_method == 'OAuth2':
            options = '--insecure --overwrite --access-token {0} -s {1} {2} {3}'.format(opts.token, opts.fts, src, dst)
        else:
            options = '--insecure --overwrite -s {0} {1} {2}'.format(opts.fts, src, dst)
        start = datetime.utcnow()
        var = os.system('python ' + script_transfer_path + ' ' + options + ' >/dev/null 2>&1')
        if var != 0:
            log.error("FTS job submission failed")
            exit(-1)
        end = datetime.utcnow()
        duration += (end - start)

    duration_seconds = duration.seconds + (duration.microseconds / 1000000.0)
    log.info("Total time for {0}:       {1}".format(auth_method, duration_seconds))
    log.info("Files per second for " + auth_method + ": " + str(float(opts.files_number) / duration_seconds))

def benchmark_whoami(opts, auth_method='OAuth2'):
    log.info("Starting benchmark for whoami with auth method {0}".format(auth_method))

    duration = timedelta()
    start = datetime.utcnow()
    for f in xrange(100):
        if auth_method == 'OAuth2':
            options = '--insecure --access-token {0} -s {1}'.format(opts.token, opts.fts)
        else:
            options = '--insecure --overwrite -s {0}'.format(opts.fts)
        var = os.system('python ' + script_whoami_path + ' ' + options + ' >/dev/null 2>&1')
        if var != 0:
            log.error("FTS whoami query failed")
            exit(-1)
    end = datetime.utcnow()
    duration += (end - start)

    duration_seconds = duration.seconds + (duration.microseconds / 1000000.0)
    log.info("Total time for {0}:       {1}".format(auth_method, duration_seconds))

if __name__ == "__main__":
    opt_parser = OptionParser()
    opt_parser.add_option("-f", "--files", dest="files_number", type="int",
                          default=100,
                          help="Number of files to send in a single job")
    opt_parser.add_option("--fts", dest="fts", default='certificate',
                          help="FTS server to benchmark against")
    opt_parser.add_option("--token", dest="token", default='access_token',
                          help="IAM XDC access token")
    (opts, args) = opt_parser.parse_args()
    log = setup_logging(False)

    benchmark_whoami(opts, "OAuth2")
    benchmark_whoami(opts, "X509")

    benchmark_transfer_auth(opts, "OAuth2")
    benchmark_transfer_auth(opts, "X509")
