Note that this code was developed in a MacOS Unix/Linux environment, so the instructions below may have to 
be adjusted if being run on a Windows machine.

------ INSTALLATION INSTRUCTIONS -------
1. This repo runs on Python 3.9.6 (I have not had success with v3.11)
2. Please add a 'settings.json' file with the following format with your HMIS login info:

{
    "login_info" : [
        {
            "hmis_username" : "your_username",
            "hmis_password" : "your_password"
            "salt_username" : "your_username",
            "salt_password" : "your_password",
            "output_path" : "your_filepath"
        }
    ]
}

(Don't worry, it won't run without this)

3. I'm using pip to manage dependencies, install using requirements.txt

python -m pip install -r requirements.txt

------ RUNNING INSTRUCTIONS -------
1. Download the report from the SALT Web App

2. Run the automated script on the data, this usually takes about 30-40 minutes
python salt/run_daily_data.py -f ~/Downloads/Report_by_client_02-04-2024.xlsx -a

3. Any failed entries will be put into a new excel sheet under 'salt/output'

4. Rerun this to try and automate the failed entries again
python salt/run_daily_data.py -f salt/output/Failed\ Entries\ -\ 02-18-2024.xlsx -a

5. Clean the excel sheet of failed entries to make manual entry easier
python salt/run_daily_data.py -f salt/output/Failed\ Entries\ -\ 02-18-2024.xlsx -m

------- ARGUMENT FLAGS AND THEIR MEANINGS: --------
-f, --filename: [REQUIRED] filename to be run
-a, --automate: run the bot script for automated entry
-m, --manual: cleans the excel sheet data to be more readable for manual entry
-o, --output: prints data to the terminal, good for debug use
-l, --listitems: lists all the codes of unique items i.e. BXR, SKS, TPS, etc.