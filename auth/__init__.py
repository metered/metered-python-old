# Copyright 2023 Tesserai. All rights reserved.
# Copyright 2020 The HuggingFace Team. All rights reserved.
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

import os
import logging
import sys

from getpass import getpass
from typing import Optional
from contextlib import contextmanager
from io import StringIO
from typing import IO, Generator, List, Optional, Tuple, Union

_TOKEN_URL = "https://metered.dev/api/api_LByDlDSqYRZOFEEW/subscription"
_TOKEN_ENV_VAR = 'METERED_API_KEY'
_ASCII_LOGOTYPE = """
                _                    _      _
 _ __ ___   ___| |_ ___ _ __ ___  __| |  __| | _____   __
| '_ ` _ \ / _ \ __/ _ \ '__/ _ \/ _` | / _` |/ _ \ \ / /
| | | | | |  __/ ||  __/ | |  __/ (_| || (_| |  __/\ V /
|_| |_| |_|\___|\__\___|_|  \___|\__,_(_)__,_|\___| \_/
    """

logger = logging.getLogger(__name__)

@contextmanager
def _capture_output() -> Generator[StringIO, None, None]:
    """Capture output that is printed to terminal.

    Taken from https://stackoverflow.com/a/34738440

    Example:
    ```py
    >>> with _capture_output() as output:
    ...     print("hello world")
    >>> assert output.getvalue() == "hello world\n"
    ```
    """
    output = StringIO()
    previous_output = sys.stdout
    sys.stdout = output
    yield output
    sys.stdout = previous_output

# Shell-related helpers
try:
    # Set to `True` if script is running in a Google Colab notebook.
    # If running in Google Colab, git credential store is set globally which makes the
    # warning disappear. See https://github.com/huggingface/huggingface_hub/issues/1043
    #
    # Taken from https://stackoverflow.com/a/63519730.
    _is_google_colab = "google.colab" in str(get_ipython())  # type: ignore # noqa: F821
except NameError:
    _is_google_colab = False


def is_notebook() -> bool:
    """Return `True` if code is executed in a notebook (Jupyter, Colab, QTconsole).

    Taken from https://stackoverflow.com/a/39662359.
    Adapted to make it work with Google colab as well.
    """
    try:
        shell_class = get_ipython().__class__  # type: ignore # noqa: F821
        for parent_class in shell_class.__mro__:  # e.g. "is subclass of"
            if parent_class.__name__ == "ZMQInteractiveShell":
                return True  # Jupyter notebook, Google colab or qtconsole
        return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_google_colab() -> bool:
    """Return `True` if code is executed in a Google colab.

    Taken from https://stackoverflow.com/a/63519730.
    """
    return _is_google_colab


def _is_valid_token(token: str):
    # FIXME
    return True

def save_token(token: str):
    os.environ[_TOKEN_ENV_VAR] = token

def get_token():
    os.environ.get(_TOKEN_ENV_VAR, None)

def delete_token():
    del os.environ[_TOKEN_ENV_VAR]

_path_token = f'os.environ["{_TOKEN_ENV_VAR}"]'

def login(token: Optional[str] = None) -> None:
    """Login the machine to access the Hub.

    The `token` is persisted in cache and set as a git credential. Once done, the machine
    is logged in and the access token will be available across all `huggingface_hub`
    components. If `token` is not provided, it will be prompted to the user either with
    a widget (in a notebook) or via the terminal.

    To login from outside of a script, one can also use `huggingface-cli login` which is
    a cli command that wraps [`login`].

    <Tip>
    [`login`] is a drop-in replacement method for [`notebook_login`] as it wraps and
    extends its capabilities.
    </Tip>

    <Tip>
    When the token is not passed, [`login`] will automatically detect if the script runs
    in a notebook or not. However, this detection might not be accurate due to the
    variety of notebooks that exists nowadays. If that is the case, you can always force
    the UI by using [`notebook_login`] or [`interpreter_login`].
    </Tip>

    Args:
        token (`str`, *optional*):
            User access token to generate from https://huggingface.co/settings/token.


    Raises:
        [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)
            If an organization token is passed. Only personal account tokens are valid
            to login.
        [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)
            If token is invalid.
        [`ImportError`](https://docs.python.org/3/library/exceptions.html#ImportError)
            If running in a notebook but `ipywidgets` is not installed.
    """
    if token is not None:
        _login(token)
    elif is_notebook():
        notebook_login()
    else:
        interpreter_login()


def logout() -> None:
    """Logout the machine from the Hub.

    Token is deleted from the machine and removed from git credential.
    """
    token = get_token()
    if token is None:
        print("Not logged in!")
        return
    delete_token()
    print("Successfully logged out.")


###
# Interpreter-based login (text)
###


def interpreter_login() -> None:
    """
    Displays a prompt to login to the HF website and store the token.

    This is equivalent to [`login`] without passing a token when not run in a notebook.
    [`interpreter_login`] is useful if you want to force the use of the terminal prompt
    instead of a notebook widget.

    For more details, see [`login`].
    """
    print(_ASCII_LOGOTYPE)
    if get_token() is not None:
        print(
            "    A token is already saved. Run `logout()` if you want"
        )
        print("    Setting a new token will erase the existing one.")

    print(f"    To login, `huggingface_hub` requires a token generated from {_TOKEN_URL} .")
    if os.name == "nt":
        print("Token can be pasted using 'Right-Click'.")
    token = getpass("Token: ")

    _login(token=token)


###
# Notebook-based login (widget)
###

NOTEBOOK_LOGIN_PASSWORD_HTML = """<center> <img
src=https://metered.dev/assets/favicon-96x96.png
alt='metered.dev'> <br> Immediately click login after typing your password or
it might be stored in plain text in this notebook file. </center>"""


NOTEBOOK_LOGIN_TOKEN_HTML_START = f"""<center> <img
src=https://metered.dev/assets/favicon-96x96.png
alt='metered.dev'> <br> Copy a token from <a
href="{_TOKEN_URL}" target="_blank">your metered.dev API key
page</a> and paste it below. <br> Immediately click login after copying
your token or it might be stored in plain text in this notebook file. </center>"""


NOTEBOOK_LOGIN_TOKEN_HTML_END = """
"""
# <b>Pro Tip:</b> If you don't already have one, you can create a dedicated
# 'notebooks' token with 'write' access, that you can then easily reuse for all
# notebooks. </center>"""


def notebook_login() -> None:
    """
    Displays a widget to login to the HF website and store the token.

    This is equivalent to [`login`] without passing a token when run in a notebook.
    [`notebook_login`] is useful if you want to force the use of the notebook widget
    instead of a prompt in the terminal.

    For more details, see [`login`].
    """
    try:
        import ipywidgets.widgets as widgets  # type: ignore
        from IPython.display import display  # type: ignore
    except ImportError:
        raise ImportError(
            "The `notebook_login` function can only be used in a notebook (Jupyter or"
            " Colab) and you need the `ipywidgets` module: `pip install ipywidgets`."
        )

    box_layout = widgets.Layout(display="flex", flex_flow="column", align_items="center", width="50%")

    token_widget = widgets.Password(description="Token:")
    token_finish_button = widgets.Button(description="Login")

    login_token_widget = widgets.VBox(
        [
            widgets.HTML(NOTEBOOK_LOGIN_TOKEN_HTML_START),
            token_widget,
            token_finish_button,
            widgets.HTML(NOTEBOOK_LOGIN_TOKEN_HTML_END),
        ],
        layout=box_layout,
    )
    display(login_token_widget)

    # On click events
    def login_token_event(t):
        token = token_widget.value
        # Erase token and clear value to make sure it's not saved in the notebook.
        token_widget.value = ""
        # Hide inputs
        login_token_widget.children = [widgets.Label("Connecting...")]
        try:
            with _capture_output() as captured:
                _login(token)
            message = captured.getvalue()
        except Exception as error:
            message = str(error)
        # Print result (success message or error)
        login_token_widget.children = [widgets.Label(line) for line in message.split("\n") if line.strip()]

    token_finish_button.on_click(login_token_event)


###
# Login private helpers
###


def _login(token: str) -> None:
    if not _is_valid_token(token=token):
        raise ValueError("Invalid token passed!")
    print("Token is valid.")

    save_token(token)
    print(f"Your token has been saved to {_path_token}")
    print("Login successful")

