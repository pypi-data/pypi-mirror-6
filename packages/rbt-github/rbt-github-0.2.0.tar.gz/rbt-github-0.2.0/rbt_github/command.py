#
# Copyright 2014 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from rbtools.commands import Command, CommandError, Option
from rbtools.utils.filesystem import make_tempfile, load_config, get_config_value
import collections
import email
import json
import urllib2

class Github(Command):
  """Extension to review and apply patches from Github"""
  name = 'github'
  author = 'Jake Farrell'
  description = 'Review and apply patches from Github'
  args = '<github-pull-request-id>'
  option_list = [
    Option("-c", "--commit",
               dest="commit",
               action="store_true",
               default=False,
               help="Commit using information fetched "
                    "from the pull request."),
    Option("--px",
               dest="px",
               default=None,
               help="numerical pX argument for patch"),
    Option("-p", "--print",
               dest="patch_stdout",
               action="store_true",
               default=False,
               help="print patch to stdout instead of applying"),
    Option("-o", "--owner",
               dest="owner",
               default="apache",
               help="Github repository owner to use"),
    Option("-r", "--repo",
               dest="repo",
               default=None,
               help="Github repository to use"),
  ]

  def get_patch(self, pull_request_id):
    """Return the pull request diff as a string."""
    try:
      url = "https://github.com/%s/%s/pull/%s.patch" % (self.options.owner, self.options.repo, pull_request_id)
      diff = urllib2.urlopen(url).read()
    except Exception, e:
      raise CommandError("Error getting pull request patch: %s" % e)

    return diff

  def github_pull_request_details(self, pull_request_id, keys=[]):
    """Get pull request details from the pull request json api."""
    url = "https://api.github.com/repos/%s/%s/pulls/%s" % (self.options.owner, self.options.repo, pull_request_id)
    data = json.loads(urllib2.urlopen(url).read())

    for key in keys:
      try:
        temp = data[key]
        data = temp
      except KeyError:
        return None

    return data

  def get_author_from_patch(self, patch_file):
    """Extract the Author of the patch from the patch header."""
    data = open(patch_file, 'r').read()
    msg = email.message_from_string(data)
    name, addr = email.utils.parseaddr(msg.get('from'))
    author = collections.namedtuple("author", ["fullname", "email"])
    result = author(name, addr)
    return result

  def apply_patch(self, repository_info, tool, pull_request_id, patch_file):
    """Apply patch patch_file and display results to user."""
    print ("Patch is being applied from pull request %s" % (pull_request_id))
    tool.apply_patch(patch_file, repository_info.base_path, None, self.options.px)

  def generate_commit_message(self, pull_request_id):
    """Returns a commit message based on the pull request id."""
    summary = self.github_pull_request_details(pull_request_id, ['title'])
    description = self.github_pull_request_details(pull_request_id, ['body'])

    info = []
    info.append(summary)

    if description.strip:
      info.append(description)

    info.append("This closes: #%s" % pull_request_id)
    info.append("Reviewed at https://github.com/%s/%s/pull/%s" % (self.options.owner, self.options.repo, pull_request_id))

    return '\n\n'.join(info)

  def main(self, pull_request_id):
    repository_info, tool = self.initialize_scm_tool()

    configs = [load_config()]

    if self.options.owner is None:
      self.options.owner = get_config_value(configs, 'GITHUB_OWNER', None)

    if self.options.repo is None:
      self.options.repo = get_config_value(configs, 'GITHUB_REPO', None)

    if self.options.owner is None or self.options.repo is None:
      raise CommandError("No GITHUB_REPO or GITHUB_OWNER has been configured.")

    diff = self.get_patch(pull_request_id)

    if self.options.patch_stdout:
      print diff
    else:
      try:
        if tool.has_pending_changes():
          message = 'Working directory is not clean.'

          if not self.options.commit:
            print 'Warning: %s' % message
          else:
            raise CommandError(message)
      except NotImplementedError:
          pass

      tmp_patch_file = make_tempfile(diff)
      self.apply_patch(repository_info, tool, pull_request_id, tmp_patch_file)

      if self.options.commit:
        message = self.generate_commit_message(pull_request_id)
        author = self.get_author_from_patch(tmp_patch_file)

        try:
          tool.create_commit(message, author)
          print('Changes committed to current branch.')
        except NotImplementedError:
          raise CommandError('--commit is not supported with %s' % tool.name)

