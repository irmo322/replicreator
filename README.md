# replicreator

## installation

Install python 3.8+ and execute :
> pip3 install -e .

Now you should be able to execute 'generate_web_app.py' script in demos folder.
This generates a 'statistics.csv' and a 'index.html'.

The statistic file contains statistics about the play : number of lines, words and alphanumerical 
characters for each scene and each character.

The 'index.html' file is a self-contained web app for learning the play sample.

The script uses 'replicreator_parameters.yaml' and the content of 'transcriptions' as input to compute
statistics and generate the web app.

