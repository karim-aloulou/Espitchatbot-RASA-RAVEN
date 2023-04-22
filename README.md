
## Espritchatbot
This is a chatbot designed to answer questions about Esprit University. It was created using the Rasa framework.

## Prerequirments
Python 3.4+
Virtualenv
pip

## Installation
To open the chatbot, clone the repository to your local machine:

```
git clone https://github.com/karim-aloulou/Espritchatbot.git
```
All of the following will be built into a virtualenv

open the cmd in the root folder
do : 
```
cd ../

```

Then do the follow:

```
python -m venv myenv
```

Then activate the environnement
```
myenv\Scripts\activate
```

Make sure you have Python 3.x installed on your machine. You can install the required Python libraries by running:

```
pip install rasa

```

## Usage
To use the chatbot, navigate to the Espritchatbot directory and run one of the following commands:

Run the chatbot :

```
rasa shell
```

Run the chatbot with nlu:

```
rasa shell nlu
```


Train the chat:

```
rasa train
```
## File Structure

Espritchatbot/                                                                              
├── .rasa/                                                                                  
│   ├── cache/                                                                              
│   │   ├── tmp00lirg7m/                                                                    
│   │   │   └── patterns.pkl                                                                
│   │   └── cache.db                                                                        
│   └── ...                                                                                 
├── actions/                                                                                
│   ├── __init__.py                                                                         
│   ├── actions.py                                                                          
│   └── ...                                                                                 
├── data/                                                                                   
│   ├── nlu.yml                                                                             
│   └── stories.yml                                                                         
├── models/                                                                                 
│   ├── 20230312-184216.tar.gz                                                              
│   └── ...                                                                                 
├── tests/                                                                                  
│   ├── __init__.py                                                                         
│   └── ...                                                                                 
├── config.yml                                                                              
├── credentials.yml                                                                         
├── domain.yml                                                                              
└── README.md                                                                               
