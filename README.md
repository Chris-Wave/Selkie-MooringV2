# Installation Guide

- Ensure Anaconda is installed. Use command in a terminal:

		- conda help

If conda is installed properly, this will display a message, part of which is quoted here:

usage: conda [-h] [-V] command ...

conda is a tool for managing and deploying applications, environments and packages.

- Ensure Anaconda is updated. Check the version of Python installed in your PC. Run `python --version` in the Anaconda Prompt. Ensure the version is >3.9. If it is one of the previous versions, please update anaconda by deleting the previous installation and reinstalling.  

- To use this package, clone the repository via a git pull or manually by downloading the zip folder. 


- Navigate into the directory of the downloaded code in a Anaconda Prompt. 

- Create a new environment within conda to avoid breaking your base conda installation:

		conda create -n myenv python=3.9
		conda activate myenv

- Use the following command to install all the necessary libraries:

		pip install -r requirements.txt

 

### Note
 Command terminal and Anaconda Prompt are one and the same. HOwever, the anaconda prompt uses Bash as the language which might not always be the case for Window's command terminal.