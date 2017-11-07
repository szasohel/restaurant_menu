#Project Title:

Item catalog with CRUD functionality

##Prerequisites:

To run this project:
1. Python2 or 3
2. SQLite
3. sqlalchemy
4. flask
5. vagrant virtual machine

##Files:
catalog folder:
	1. views.py
	2. model.py
	3. client_secrets.json
	template folder:
		1. catagory.html
		2. public_catagory.html
		3. edit_catagory.html
		4. delete_catagory.html
		5. item.html
		6. public_item.html
		7. edit_item.html
		8. delete_item.html
		9. login.html
	static folder:
		1. styles.css
		2. bg.jpg
		3. cont_bg.jpg

##How it works:

This project sets up a SQLite database for a fictional catalog web application.
HTML, CSS and JavaScript uses to design front end functionality. 
The provided Python script uses the sqlalchemy library perform CRUD on the database.
user can brows the site. to perform CRUD operation they have to log in. once 
logged in  they can create their own catagory, item. the can only edit and delete the
item created by them. 

##Steps for running the program:

1. VirtualBox is the software that actually runs the virtual machine. 
   You can download it from virtualbox.org. Install the platform 
   package for your operating system.
2. Vagrant is the software that configures the VM and lets you share 
   files between your host computer and the VM's filesystem. Download it 
   from vagrantup.com. Install the version for your operating system.
3. The database is supplied inside catalog folder named itemcatalog.db
5. Open a Linux-like command line terminal (e.g. Git Bash, MacOS terminal, etc.) 
6. Start the virtual machine using command 
			vagrant up
7. Login to the VM using 
			vagrant ssh
8. Using cd command go to the path where views.py was saved
9. Enter the following command to execute the program
			python views.py
10. Open a browser and enter folloeing address in the browser
			http://localhost:5000
11. You can now use the app in your local machine

##Git access:

https://github.com/szasohel/item_catalog.git

##Created by:

Sayed Zahed Abdullah Sohel
