# Copyright 2014 OpenCore LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import grp
import json
import logging
import os
import os.path
import pwd
import re
import shutil
import stat
import sys
import time
from distutils import spawn
from string import Template
from subprocess import Popen, PIPE
from ferry.options import CmdHelp

def get_ferry_home():
    if 'FERRY_HOME' in os.environ:
        return os.environ['FERRY_HOME']
    else:
        return os.path.dirname(os.path.dirname(__file__)) + '/ferry'

FERRY_HOME=get_ferry_home()
DEFAULT_IMAGE_DIR=FERRY_HOME + '/dockerfiles'
DEFAULT_KEY_DIR=FERRY_HOME + '/key'
GLOBAL_KEY_DIR=DEFAULT_KEY_DIR
# DEFAULT_DOCKER_REPO='%s' % os.environ['USER']
DEFAULT_DOCKER_REPO='drydock'
DOCKER_CMD='docker-ferry'
DOCKER_SOCK='unix:////var/run/ferry.sock'
DOCKER_DIR='/var/lib/drydock'
DOCKER_PID='/var/run/ferry.pid'
DEFAULT_MONGO_DB='/var/lib/drydock/mongo'
DEFAULT_MONGO_LOG='/var/lib/drydock/mongolog'
DEFAULT_REGISTRY_DB='/var/lib/drydock/registry'
DEFAULT_DOCKER_LOG='/var/lib/drydock/docker.log'

class Installer(object):

    def install(self, args):
        self._start_docker_daemon()

        if '-k' in args:
            GLOBAL_KEY_DIR = self.fetch_image_keys(args['-k'][0])
        else:
            GLOBAL_KEY_DIR = self.fetch_image_keys()

        if '-u' in args:
            # We want to re-build all the images. 
            logging.warning("performing forced rebuild")
            self.build_from_dir(DEFAULT_IMAGE_DIR, DEFAULT_DOCKER_REPO )
        else:
            # We want to be selective about which images
            # to rebuild. Useful if one image breaks, etc. 
            to_build = self.check_images(DEFAULT_IMAGE_DIR,
                                         DEFAULT_DOCKER_REPO)
            if len(to_build) > 0:
                self.build_from_list(to_build, 
                                     DEFAULT_IMAGE_DIR,
                                     DEFAULT_DOCKER_REPO)

    def start_web(self):
        self._start_docker_daemon()

        # Check if the Mongo directory exists yet. If not
        # go ahead and create it. 
        try:
            if not os.path.isdir(DEFAULT_MONGO_DB):
                os.makedirs(DEFAULT_MONGO_DB)
                self._change_permission(DEFAULT_MONGO_DB)
            if not os.path.isdir(DEFAULT_MONGO_LOG):
                os.makedirs(DEFAULT_MONGO_LOG)
                self._change_permission(DEFAULT_MONGO_LOG)
        except OSError as e:
            logging.error("Could not start ferry servers.\n") 
            logging.error(e.explanation)
            sys.exit(1)

        # Start the Mongo server.
        mongo_data = '/service/data'
        mongo_log = '/service/logs'
        cmd = DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' run -d -v %s:%s -v %s:%s %s/mongodb' % (DEFAULT_MONGO_DB, mongo_data, 
                                                                                            DEFAULT_MONGO_LOG, mongo_log, 
                                                                                            DEFAULT_DOCKER_REPO)
        logging.warning(cmd)
        child = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        output = child.stderr.read().strip()
        if re.compile('[/:\s\w]*Can\'t connect[\'\s\w]*').match(output):
            logging.error("Ferry docker daemon does not appear to be running")
            sys.exit(1)
        elif re.compile('Unable to find image[\'\s\w]*').match(output):
            logging.error("Ferry mongo image not present")
            sys.exit(1)

        # Need to get Mongo connection info and store in temp file. 
        container = child.stdout.read().strip()
        cmd = DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' inspect %s' % container
        logging.warning(cmd)
        output = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
        output_json = json.loads(output.strip())
        ip = output_json[0]['NetworkSettings']['IPAddress']
        self._touch_file('/tmp/mongodb.ip', ip)

        # Sleep a little while to let Mongo start receiving.
        time.sleep(2)

        # Start the HTTP servers
        my_env = os.environ.copy()
        my_env['MONGODB'] = ip
        logging.warning("starting http servers on port 4000 and mongo %s" % ip)
        cmd = 'gunicorn -e FERRY_HOME=%s -t 3600 -w 3 -k gevent -b 127.0.0.1:4000 ferry.http.httpapi:app &' % FERRY_HOME
        Popen(cmd, stdout=PIPE, shell=True, env=my_env)

    def stop_web(self):
        # Shutdown the mongo instance
        if os.path.exists('/tmp/mongodb.ip'):
            f = open('/tmp/mongodb.ip', 'r')
            ip = f.read().strip()
            cmd = 'ssh root@%s /service/bin/mongodb stop' % ip
            logging.warning(cmd)
            output = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
            os.remove('/tmp/mongodb.ip')

        # Kill all the gunicorn instances. 
        logging.warning("stopping http servers")
        cmd = 'ps -eaf | grep httpapi | awk \'{print $2}\' | xargs kill -15'
        Popen(cmd, stdout=PIPE, shell=True)
        
    def _copytree(self, src, dst):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    def _change_permission(self, location):
        uid = pwd.getpwnam("root").pw_uid
        gid = grp.getgrnam("docker").gr_gid
        os.chown(location, uid, gid)

        if os.path.isdir(location):        
            os.chmod(location, 
                     stat.S_IRUSR |
                     stat.S_IWUSR |
                     stat.S_IXUSR | 
                     stat.S_IRGRP |
                     stat.S_IWGRP |
                     stat.S_IXGRP |
                     stat.S_IROTH)
            for entry in os.listdir(location):
                self._change_permission(os.path.join(location, entry))
        else:
            # Check if this file has a file extension. If not,
            # then assume it's a binary.
            s = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
            if len(location.split(".")) == 1:
                s |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.chmod(location, s)

    """
    Ask for the key directory.
    """
    def fetch_image_keys(self, key_dir=None):
        if key_dir and os.path.exists(key_dir):
            return key_dir
        else:
            return DEFAULT_KEY_DIR

    """
    Check if the dockerfiles are already built. 
    """
    def check_images(self, image_dir, repo):
        if self._docker_running():
            build_images = []
            for f in os.listdir(image_dir):
                dockerfile = image_dir + '/' + f + '/Dockerfile'
                image_name = self._check_dockerfile(dockerfile, repo)
                if image_name:
                    build_images.append(image_name)
            return build_images
        else:
            logging.error("ferry daemon not started")

    """
    Build the docker images
    """
    def build_from_list(self, to_build, image_dir, repo):
        if self._docker_running():
            built_images = {}
            for f in os.listdir(image_dir):
                dockerfile = image_dir + '/' + f + '/Dockerfile'
                image = self._get_image(dockerfile)
            
                if image in to_build:
                    logging.warning("building image " + image)
                    self._transform_dockerfile(image_dir, f, repo)

            for f in os.listdir("/tmp/dockerfiles/"):
                dockerfile = '/tmp/dockerfiles/' + f + '/Dockerfile'
                self._build_image(dockerfile, repo, built_images)

            # After building everything, get rid of the temp dir.
            shutil.rmtree("/tmp/dockerfiles")
        else:
            logging.error("ferry daemon not started")

    """
    Build the docker images
    """
    def build_from_dir(self, image_dir, repo):
        if self._docker_running():
            built_images = {}
            for f in os.listdir(image_dir):
                self._transform_dockerfile(image_dir, f, repo)
            for f in os.listdir("/tmp/dockerfiles/"):
                dockerfile = "/tmp/dockerfiles/" + f + "/Dockerfile"
                self._build_image(dockerfile, repo, built_images, recurse=True)

            # After building everything, get rid of the temp dir.
            shutil.rmtree("/tmp/dockerfiles")
        else:
            logging.error("ferry daemon not started")

    def _docker_running(self):
        return os.path.exists('/var/run/ferry.sock')

    def _check_dockerfile(self, dockerfile, repo):
        image = self._get_image(dockerfile)
        qualified = DEFAULT_DOCKER_REPO + '/' + image

        cmd = DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' inspect ' + qualified + ' 2> /dev/null'
        output = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
        if output.strip() == '[]':
            return image
        else:
            return None

    def _transform_dockerfile(self, image_dir, f, repo):
        if not os.path.exists("/tmp/dockerfiles/" + f):
            shutil.copytree(image_dir + '/' + f, '/tmp/dockerfiles/' + f)
    
        out_file = "/tmp/dockerfiles/" + f + "/Dockerfile"
        out = open(out_file, "w+")
        changes = { "USER" : repo,
                    "DOCKER" : grp.getgrnam("docker").gr_gid }
        for line in open(image_dir + '/' + f + '/Dockerfile', "r"):
            s = Template(line).substitute(changes)
            out.write(s)
        out.close()

    def _build_image(self, f, repo, built_images, recurse=False):
        base = self._get_base(f)
        if recurse and base != "base":
            image_dir = os.path.dirname(os.path.dirname(f))
            dockerfile = image_dir + '/' + base + '/Dockerfile'
            self._build_image(dockerfile, repo, built_images, recurse)

        image = os.path.dirname(f).split("/")[-1]
        if not image in built_images:
            built_images[image] = True
            self._compile_image(image, repo, os.path.dirname(f))

    def _get_image(self, dockerfile):
        for l in open(dockerfile, 'r'):
            if l.strip() != '':
                s = l.split()
                if len(s) > 0:
                    if s[0].upper() == 'NAME':
                        return s[1].strip()
        return None

    def _get_base(self, dockerfile):
        base = None
        for l in open(dockerfile, 'r'):
            s = l.split()
            if len(s) > 0:
                if s[0].upper() == 'FROM':
                    base = s[1].strip().split("/")
                    return base[-1]
        return base

    def _compile_image(self, image, repo, image_dir):
        # Copy over the keys. 
        shutil.copy(GLOBAL_KEY_DIR + '/id_rsa.pub', image_dir)
    
        # Now build the image. 
        cmd = DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' build -privileged -t' + ' %s/%s %s' % (repo, image, image_dir)
        logging.warning(cmd)
        output = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
        logging.debug(output)

    def _clean_images(self):
        cmd = DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' | grep none | awk \'{print $1}\' | xargs ' + DOCKER_CMD + ' -H=' + DOCKER_SOCK + ' rmi'
        Popen(cmd, stdout=PIPE, shell=True)

    def _is_running_btrfs(self):
        logging.warning("checking for btrfs")
        cmd = 'cat /etc/mtab | grep %s | awk \'{print $3}\'' % DOCKER_DIR
        output = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
        return output.strip() == "btrfs"

    def _start_docker_daemon(self):
        # Check if the docker daemon is already running
        try:
            if not self._docker_running():
                bflag = ''
                if self._is_running_btrfs():
                    bflag = ' -s btrfs'

                # We need to fix this so that ICC is set to false. 
                icc = ' --icc=true'
                cmd = 'nohup ' + DOCKER_CMD + ' -d' + ' -H=' + DOCKER_SOCK + ' -g=' + DOCKER_DIR + ' -p=' + DOCKER_PID + bflag + icc + ' 1>%s  2>&1 &' % DEFAULT_DOCKER_LOG
                logging.warning(cmd)
                Popen(cmd, stdout=PIPE, shell=True)

                # Wait a second to let the docker daemon do its thing.
                time.sleep(2)
        except OSError as e:
            logging.error("could not start docker daemon.\n") 
            logging.error(e.explanation)
            sys.exit(1)

    def _stop_docker_daemon(self):
        if self._docker_running():
            logging.warning("stopping docker daemon")
            cmd = 'pkill -f ferry'
            Popen(cmd, stdout=PIPE, shell=True)
            os.remove('/var/run/ferry.sock')

    def _touch_file(self, file_name, content):
        f = open(file_name, 'w+')
        f.write(content)
        f.close()
