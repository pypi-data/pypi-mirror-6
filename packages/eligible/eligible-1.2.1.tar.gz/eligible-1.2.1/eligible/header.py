import eligible
import json
import platform

_python_version = "{implementation} {version} ({build})".format(implementation=platform.python_implementation(),
                                                                version=platform.python_version(),
                                                                build=', '.join(platform.python_build()))

ua = {'bindings_version': eligible.__version__,
      'lang': 'python',
      'lang_version': _python_version,
      'platform': platform.python_compiler(),
      'publisher': 'eligible',
      'uname': ', '.join(platform.uname())}

headers = {'x-eligible-client-user-agent': json.dumps(ua),
           'user_agent': 'Eligible/v1 PythonBindings/{}'.format(eligible.api_version),
           'authorization': 'Bearer {}'.format(eligible.api_key),
           'content_type': 'application/x-www-form-urlencoded',
           'eligible_version': eligible.api_version}
