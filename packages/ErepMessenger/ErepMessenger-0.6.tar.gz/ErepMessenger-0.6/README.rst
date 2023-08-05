Erepublik Messenger
===================

This application makes it possible to send mass in game messages for the online game Erepublik.

Installation
------------

First you should have Python 2.7 installed. You can get it `here`_

.. _here: http://www.python.org/getit/releases/2.7.6/

Just download the installer for your operating system.

If you are on Mac OS X you will need to install `Tcl/Tk`_ also. Just download and install the recommended `Tcl/Tk`_ for your operating system.

.. _Tcl/Tk: http://www.python.org/download/mac/tcltk/

After Python(and Tcl/Tk on Mac OS X) is installed:

1. Download the latest ErepMessenger-x.x.tar.gz file
2. Extract all the files to anywhere you want
3. Open up a command prompt/terminal (Windows: Included is a file called ``install.bat`` you can skip steps 3 - 5 by double clicking this file)
    Windows: type in "Command Prompt" in the search box in the start menu then double click "Command Prompt" or Start->All Programs->Accessories->Command Prompt
    Mac OS X: open Finder then go to Applications->Utilities and find the Terminal application
    Linux: press CTRL-ALT-T
4. Change directory to the folder you extracted (this folder will contain a file named ``setup.py``)
    cd ``"the path to the folder"``
    example: ``cd C:/erepmessenger-0.9``
5. Run the ``setup.py`` script from the command prompt/terminal
    Windows: ``setup.py install``
    Mac OS X and Linux: ``python setup.py install``
6. Now run the program!
    Windows: Just double click ``erepmessenger.pyw`` in the ``erepmessenger`` folder (You can make a shortcut to the file and place it anywhere you like)
    Mac OS X and Linux: Open up the terminal to the path of ``erepmessenger.pyw`` and enter ``python erepmessenger.pyw`` (Included is a file called ``run`` you can make a link/alias to the ``run`` file and place it anywhere you like. Remember to make the file executable: ``chmod +x /path/to/run``)

Using the Messenger
-------------------

When you start up Erepublik Messenger you will see a simple GUI.
There is a menubar at the top with the options to "Start" and "Exit" and below that that you will see seperate text boxes for ID lists, your message subject, your message body, and there is a "Send" button.

To begin using the program press "Start".
You will be prompted for your Erepublik login information.
Once you are logged into Erepublik succesfully you will see the Messenger login prompt.
Here you may log in, register, or recover your Messenger password.
To register or recover your password just enter your Erepublik ID number and press the appropiate button.
After registering or recovering your password will be instantly sent to your Erepublik inbox.
Once you have your Erepublik ID number and password filled in you can login to the Messenger.

Logging into the Messenger is necessary to be able to control access to it.
In game eUSA has several enemies and this messenger should only be used by eUSA and friends.
If an enemy of eUSA tries to use it they can be easily locked out!

Once you are logged into both Erepublik and the Messenger you can now fill out the Messenger form.
You may fill out the ID list with either line seperated or comma seperated lists.
Any dead or non existent IDs entered will automatically be sorted out.
Then enter your subject and message.
Keep in mind the message body is limited to 2000 characters!
An error will appear if you try to send a message longer than 2000 characters.

Also if you do not want to fill in your login information each time you use the app you can edit the file ``config.cfg`` with a text editor.
Don't use anything like Word.
Just use a basic text editor like notepad(Windows), gedit(Linux), or textedit(Mac OS X)..

Mac OS X Users
--------------

If any of these instructions are not correct please let me know how to fix it!

I have not done any testing on Mac OS X I obtained all this information from Google searches.
