=========================================
Kaa tutorial
=========================================

インストール
============

Ubuntu linuxの場合
------------------

Python3.3のインストール
++++++++++++++++++++++++

kaaには、Python 3.3以降の環境が必要となります。Python 3.3パッケージが用意されていない Ubuntu 12.04 LTS などでは、以下の手順でPython 3.3をインストールします。Python3.3がインストール済みなら、次の「`必須ライブラリと kaa のインストール`_」に進んでください。

.. code:: sh

    $ sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev libncurses5-dev libncursesw5-dev
    $ wget http://www.python.org/ftp/python/3.3.3/Python-3.3.3.tgz
    $ tar xzf ./Python-3.3.3.tgz
    $ cd Python-3.3.3
    $ ./configure
    $ make
    $ sudo make install


次に、Pythonのパッケージ管理ツール `setuptools <https://pypi.python.org/pypi/setuptools>`_ をインストールします。

.. code:: sh

    $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    $ sudo python3.3 ez_setup.py


必須ライブラリと kaa のインストール
+++++++++++++++++++++++++++++++++++

kaaで必要なライブラリをインストールします。

    $ sudo apt-get install build-essential libncurses5-dev libncursesw5-dev

PyPIより、kaa をインストールします。

.. code:: sh

   $ sudo easy_install3 -U kaaedit


Mac OS Xの場合
------------------

Python3.3のインストール
++++++++++++++++++++++++

kaaには、Python 3.3以降の環境が必要となります。Python 3.3がインストールされていなければ、Homebrew などを利用してインストールしてください。Python3.3がインストール済みなら、次の「`kaaのインストール`_」に進んでください。

Python3 のインストールには、XCode Command Line Tools が必要となります。未インストールであれば、事前に https://developer.apple.com/downloads/index.action よりインストールしてください。

.. code:: sh

    $ brew install python3

次に、Pythonのパッケージ管理ツール `setuptools <https://pypi.python.org/pypi/setuptools>`_ をインストールします。

.. code:: sh

    $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    $ python3.3 ez_setup.py


kaaのインストール
++++++++++++++++++

PyPIより、kaa をインストールします。

.. code:: sh

   $ easy_install3 -U kaaedit

環境設定
============

キーボード設定
----------------

kaaでは、`alt+k` のような alt キーを使った操作を利用します。最近のWindows や Linux のターミナルエミュレータではそのまま利用できますが、Mac OS X のターミナルやiTermでは、以下の設定が必要になります。

Mac OS X のターミナルの場合 :

1. 「環境設定」メニューを開く
2. 「設定」タブを開く
3. 「キーボード」タブを開く
4. 「メタキーとして option キーを使用」をチェックする

iTermの場合 :

1. 「Preferences」メニューを開く
2. 「Profiles」タブを開く
3. 「Keys」タブを開く
4. 「`Left option Key acts as: +Esc.`」 ボタンと「`Right option Key acts as: +Esc.`」 ボタンをチェックする

Gnome terminal では、f1 キーでメニューを表示する場合は次のように設定します。

1. 「Edit | Keyboard shortcuts」メニューを開く
2. ショートカットに「Help/Contents」が表示されるまでスクロールし、f1キーを別のキーに変更する。

色設定
-------------

kaaは256色モードをサポートしていますが、256色モードを使えるようにするには、ターミナル設定の変更が必要となる場合があります。 Max OS Xのターミナルの場合、

1. 「環境設定」メニューを開く
2. 「詳細」タブを開く
3. 「ターミナルの宣言方法」で、「`xterm-256color` 」を選択する

iTermでは、次のように設定します。

1. 「Preferences」メニューを開く
2. 「Profiles」タブを開く
3. 「Terminal」タブを開く
4. 「`Report terminal type`」で、「`xterm-256color`」を選択する

これ以外のターミナルエミュレータでは、手動での端末種別設定が必要な場合があります。 Gnome terminalなどでは、`~/.bashrc` ファイルに、次の一行を追加してください。

.. code:: sh

    export TERM=xterm-256color

ターミナルの設定については、http://www.pixelbeat.org/docs/terminal_colours/#256 などを参考に256色モードを有効にしてください。


kaaの基本操作
===============

コマンドラインより、kaa を起動します。

.. code:: sh

    $ kaa

アルファベットや数字キーを叩くと、文字がそのまま入力されます。カーソル移動は、カーソルキーを使用するか、以下のキーで移動します。

+--------------------+------------------------------------------------+
| 左、Control+b      | カーソル左                                     |
+--------------------+------------------------------------------------+
| 右, Control+f      | カーソル右                                     |
+--------------------+------------------------------------------------+
| 上                 | カーソル上                                     |
+--------------------+------------------------------------------------+
| 下                 | カーソル下                                     |
+--------------------+------------------------------------------------+
| Control+p          | 1行上の物理行に移動                            |
+--------------------+------------------------------------------------+
| Control+n          | 一行下の物理行に移動                           |
+--------------------+------------------------------------------------+


メニュー操作
-------------------

`f1` キー又は `alt+/` キーでメニューを表示します。もし表示されない場合は、「`キーボード設定`_」を参照し、設定を見なおしてください。

メニューは、画面下端に次のように表示されます

::

    [File]/[Edit]/[Code]/[Macro]/[Tools]/[Window]

画面では、メニュー項目には下線付きで表示されている文字があり、その文字をそのまま、又はaltキーと同時に押すと、メニューが選択されます。例えば、このメニューでは、`f` キーを入力すると `File` メニューが選択され、サブメニュー ::

    New/Open/File Info/View Diff/Save/Save As/Close/Save all/Close all/[Recently]/Quit

が表示されます。


ファイル操作
-----------------

編集中のファイルを保存するときには、メニューから ``File -> Save`` を選択してファイル選択画面を表示します。途中で終了する場合はエスケープキーを押してください。。

この画面では、カレントディレクトリのファイルと子ディレクトリの一覧が表示されます。文字を入力すると、入力した文字列を含むファイルのみを検索して表示し、`tab` キーと `shift+tab` キーで一覧からファイル名を選択できます。ファイル名が決定したら `Enter` キーでファイルを保存します。

別のファイルを編集する場合は、メニューから ``File -> Open`` を選択し、ファイル選択画面からファイルを選択します。ファイルの編集が終了したら、 ``File -> Close`` でファイルを閉じます。

この時、ファイルが変更されていれば、::

    Save file before close? [TUTORIAL-JA.rst]:  Yes/No/Cancel/View Diff

と表示され、Y,N,C,D の何れかを入力します。Y(Yes)の場合はファイルが保存され、N（No)の場合は保存せずにファイルを閉じます。C(Cancel)の場合はファイルを閉じずに編集を続行し、D(View Diff)の場合はディスク上のファイルと編集中のテキストの差分を表示します。


ウィンドウ操作
-----------------

複数のファイルを同時に開いているときは、メニューの ``File -> Window -> Frame list`` でファイルの一覧を表示し、カーソルキーでファイルを選択できます。

画面を縦横に分割し、同じファイルの別々の位置を同時に編集できます。画面を縦に分割するときはメニューの ``File -> Window -> Split Vert``、横に分割するときは ``File -> Window -> Split Horz`` を選択します。

分割したウィンドウ間は、``File -> Window -> Next window`` と ``File -> Window -> Prev window`` で移動できます。


分割したウィンドウに別のファイルを表示する場合、``File -> Window -> Switch File`` 又は `alt+w` キーでメニューを表示し、新しいファイルを選択します。

::

    Switch file/New file here/Open file here/Recently used Files/Recently used Dirs

分割したウィンドウは、``File -> Window -> Join`` で結合し、ひとつのウィンドウに戻ります。


kaaを終了する
--------------------

kaaを終了するときは、メニューから ``File -> Quit`` を選択します。


Pythonデバッガ
===============

kaa を使って、Pythonスクリプトのデバッグを行います。 kaa の実行には Python3.3 以降が必要ですが、デバッグの対象となるスクリプトは Python 2.6 〜 3.x 上で起動し、デバッグできます。

デバッグを行うには、まずデバッグ対象のスクリプトを、デバッグ用のスクリプトで起動します。デバッグ用のスクリプトは、PyPI からインストールします。

.. code:: sh

    $ sudo easy_install -U kaadbg


kaa でメニューの ``Tools -> Python Debugger Server`` を選択し、ポート番号 28110 を指定して Pythonデバッガを起動します。デバッガウィンドウが表示されるので、そのまま別のターミナルウィンドウを起動します。

新しく起動したターミナルで、デバッグを行う Python インタープリタを指定し、スクリプトを実行します。ここでは Python2.7 を使って、`myscript.py` というスクリプトをデバッグしています。

.. code:: sh

    $ python2.7 -m kaadbg.run myscript.py arg1


スクリプトを開始すると、kaa 上で `myscript.py` が開きます。ここで、`alt+s` (Step) キーを押すと、一行ずつステップ実行します。

デバッグ画面でエスケープキーを押し、`myscript.py` の適当な行で ``f8`` キーを押すと、その行にブレークポイントが設定されます。メニューの ``Tools -> Python Debugger Server`` を選択してデバッガ画面を表示し、`alt+c` (Continue) キーを押すと、実行を再開してブレークポイントを設定した位置で停止します。

