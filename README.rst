================================
huarache
================================


development
-----------

setup::

  $ python3.14t -m venv env314t
  $ . env314t/bin/activate
  (venv)$ pip install 'pip==26.1'
  (venv)$ pip install --uploaded-prior-to=P7D -U pip setuptools
  (venv)$ pip install --uploaded-prior-to=P7D -e '.[develop]'
  (venv)$ pip list --format=freeze --exclude-editable $(pip list --format=freeze --editable | awk -F== '{print("--exclude="$1)}') > constraints.txt


code format::

  (venv)$ tox -e codeformat


run tests::

  (venv)$ tox


.. EOF
