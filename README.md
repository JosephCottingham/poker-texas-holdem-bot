[Medium Article](https://medium.com/@josephcottingham/my-attempt-at-writing-a-poker-bot-c53c9ccf9960)

## Preprocessing

To run preprocessing the raw game logs must be present in 'raw-data' as '.txt' files and a pickle of the Hand Classication Model must be present in the source folder under the name 'hand-classication-model.pickle'

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 run.py
```

All data will be written to 'data-out'

## Models

```
conda env create -f python-venv.yml
```

Utlizing the Anaconda Navigator run the .ipynb files with the poker enviroment.

## Game-Decision-Model 
    Data is pulled from the 'data' directory.

    All data is expected to be a csv with the file format '*.csv'

## Hand-Classication-Model
    Data is pulled from the 'data' directory.

    All generated models are saved as pickled objects in the 'pickled_models' directory.