spojcmd  (Rachit Nimavat)
=========================

Credits
---------------
I have taken [spoj](https://github.com/nyamba/spoj) by [Nyambayar Turbat](https://github.com/nyamba) as the seed.


Config File (optional)
---------------
	Create a file named .spojcmdrc  in your home folder, with the following  contents -

	[user]
	user_name = YOUR_USERNAME
	password = YOUR_PASSWORD
	wait_time = 4	(time interval in seconds for querying status of your submission)
	pyver = 2.7	(version for python compiler - 2.7 / 3.2.3 / nbc )
	cppver = 4.3.2	(version for gcc cpp compiler - 4.3.2 / 4.0.0.0-8 )
	cver = 4.3.2	(version for gcc c compiler - 4.3.2 / 99 )
	pasver = fpc	(version for pascal compiler - fpc / gpc )

	Note that, all these options are optional except [user] section line


Setup Instructions
--------------

First, get python-pip. Then install spojcmd by it. Resolve unsatisfied dependencies, if any.

    sudo apt-get install python-pip
    sudo pip install spojcmd


Login to SPOJ
---------------

Login to SPOJ like this:

	spojcmd login <username>
	password: <password>


User Status
---------------------

To get any user's solved/unsolved problems:

	spojcmd status <username>

For your own stats:

	spojcmd status
	


Submit problem on SPOJ (The most fun part)
--------------

tackle is your command. The problem name should match its id on SPOJ (case insensitive). The compiler will be guessed by looking at the extention, but you should add the entry in ~/.spojcmdrc if you are using non-default compilers (like python 3.2.3). If you leave the problem name blank, the most recent code will be submitted, (it would ignore input/output/exec files (hopefully :P ))

	spojcmd tackle problem_id.cpp

After submitting, wait till a flashing green (well, upto terminal standards) ACCEPTED is displayed.


List problems
---------

Just for the sake of completeness, list argument lists the problems based on some filters. --sort option denoted on which column the list should be sorted. If it is positive, ascending order else descending. Available options: 

	1 - problem id
	2 - problem name
	5 - solution id
	6 - users count who solved it
	7 - percentage of valid solutions

Use the option like this:

    spojcmd list --page=2 --sort=1 --problem_set=classical


Get problem statemnt (Beta)
--------------------

Get problem statement by desc argument.

    spojcmd desc problem_id
