insolater
=========

A simple version control system for small personal projects.
insolater has an easy to use interface to save, open, and transfer versions
of your work.

Installation
------------
::

  pip install insolater

Examples
--------
In a python script:

.. code-block:: python

  import insolater
  insolater.init()
  insolater.save_version('v1')
  insolater.change_version('v1')
  # Modify some files
  insolater.push_version('user@host:path_to_dir_for_version')
  insolater.pull_version('user@host:path_to_dir_for_version', 'pulled_ver')
  insolater.current_version()
  insolater.change_version('original')
  # Changes are not present.
  insolater.change_version('pulled_ver')
  # Changes are back.
  insolater.delete_version('v1')
  insolater.all_versions()
  insolater.exit(True)
  # .insolater_repo is deleted and files are in their original condition.

Running from command line::

  $ ls *
  fa  fb  test_scipt.sh

  d:
  fa  fc
  $ inso init
  Initialized repository with versions: original
  $ inso list
  * original
  $ echo data > f
  $ rm fb
  $ echo data >> fa
  $ echo data >> d/fa
  $ inso save changes
  Version changes created and opened
  $ ls *
  f  fa  test_scipt.sh

  d:
  fa  fc
  $ inso open original
  Switched to original
  $ ls *
  fa  fb  test_scipt.sh

  d:
  fa  fc
  $ cat fa
  old data a
  $ cat d/fa
  old data da
  $ inso open changes
  Switched to changes
  $ ls *
  f  fa  test_scipt.sh

  d:
  fa  fc
  $ cat fa
  old data a
  data
  $ cat d/fa
  old data da
  data
  $ cat f
  data
  $ ls ~/test_changes
  $ inso save changes2
  Version changes2 created and opened
  $ inso list
    original
  * changes2
    changes
  $ inso open changes
  Switched to changes
  $ inso rm changes2
  Version changes2 deleted
  $ inso list
    original
  * changes
  $ inso push $USER@localhost:~/test_changes/
  user@localhost's password:
  f     transfered
  fa    transfered
  d     transfered
  test_scipt.sh     transfered

  $ inso exit
  Do you want to discard all changes (y/[n]): y
  Session Ended
  $ ls ../test_changes/ ../test_changes/d
  ../test_changes/:
  d  f  fa  test_scipt.sh

  ../test_changes/d:
  fa  fc
  $ ls *
  fa  fb  test_scipt.sh

  d:
  fa  fc
  $ cat d/fa
  old data da
  $ inso init $USER@localhost:~/test_changes/
  user@localhost's password: 
  Initialized repository with versions: original
  $ inso list
  * original
  $ ls *
  f  fa  test_scipt.sh

  d:
  fa  fc
  $ cat d/fa
  old data da
  data
  $ inso -f exit
  Session Ended
  $ cat d/fa
  old data da

